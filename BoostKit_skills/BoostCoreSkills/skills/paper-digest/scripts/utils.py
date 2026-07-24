"""Shared utilities: LLM client, archive management, fetchers, config."""
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple
from openai import OpenAI

log = logging.getLogger(__name__)


class BudgetExceeded(Exception):
    """Raised when cumulative LLM token usage exceeds max_budget."""


class LLMClient:
    """DeepSeek API wrapper with token budget guard."""

    def __init__(self, api_key: str, max_budget: int = 200_000,
                 base_url: str = "https://api.deepseek.com/v1",
                 model_flash: str = "deepseek-chat",
                 model_strong: str = "deepseek-reasoner"):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.max_budget = max_budget
        self.tokens_used = 0
        self.model_flash = model_flash
        self.model_strong = model_strong

    def _resolve_model(self, model: str) -> str:
        if model == "flash":
            return self.model_flash
        if model == "strong":
            return self.model_strong
        return model  # passthrough

    def _raw_call(self, prompt: str, model: str, max_tokens: int = 2000,
                  json_mode: bool = False) -> Tuple[str, int]:
        kwargs = {
            "model": self._resolve_model(model),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        resp = self.client.chat.completions.create(**kwargs)
        text = resp.choices[0].message.content or ""
        used = resp.usage.total_tokens if resp.usage else len(text) // 4
        return text, used

    def call(self, prompt: str, model: str = "flash", max_tokens: int = 2000,
             json_mode: bool = False) -> Tuple[str, int]:
        """Call LLM and track tokens.

        Pre-flight check: if we already used more than the budget, refuse
        the next call. We can't predict actual usage of this call ahead of
        time, but this prevents runaway re-entry once we've crossed the line.
        Cumulative count is still updated after the call.
        """
        if self.tokens_used > self.max_budget:
            raise BudgetExceeded(
                f"Token budget exceeded before next call: "
                f"{self.tokens_used} > {self.max_budget}"
            )
        text, used = self._raw_call(prompt, model, max_tokens, json_mode)
        self.tokens_used += used
        if self.tokens_used > self.max_budget:
            raise BudgetExceeded(
                f"Token budget exceeded: {self.tokens_used} > {self.max_budget}"
            )
        return text, used


class CLISubprocessLLM:
    """Generic LLM backend that shells out to any local CLI tool.

    Works with Claude Code (`claude -p ...`), Gemini CLI (`gemini -p ...`),
    Codex CLI, or any agent-CLI that follows the "binary + prompt-arg +
    model-arg" pattern. Authentication is whatever the chosen CLI uses
    (Claude Code subscription OAuth, Gemini API key in env, etc.) — this
    class doesn't manage credentials.

    All CLI-specific knobs come in via constructor args so the same code
    handles every backend. See `config.yaml` `llm.cli_backend` for examples.

    Per-call overhead is dominated by subprocess spawn + CLI startup +
    re-auth, so this backend is best for smoke tests / moderate runs, not
    huge `standard` / `deep` runs over hundreds of papers.

    Token tracking is approximate (4 chars/token heuristic): most CLIs
    don't surface a structured usage object on stdout.
    """

    TIMEOUT_FLASH = 120
    TIMEOUT_STRONG = 240

    def __init__(self, max_budget: int = 200_000,
                 binary: str = "claude",
                 prompt_arg: str = "-p",
                 model_arg: str = "--model",
                 model_map: Optional[dict] = None,
                 extra_args: Optional[List[str]] = None,
                 timeout_flash: int = TIMEOUT_FLASH,
                 timeout_strong: int = TIMEOUT_STRONG,
                 json_mode_hint: Optional[str] = None):
        """All CLI specifics are configurable.

        Args:
            binary:        CLI executable name on PATH (claude / gemini / codex)
            prompt_arg:    flag preceding the prompt string (`-p` / `--prompt`)
            model_arg:     flag preceding the model name; pass "" to omit
            model_map:     {"flash": <cli model name>, "strong": <cli model name>}
                           Defaults to Claude Code's (haiku / sonnet).
            extra_args:    additional flags always appended (e.g.
                           ["--no-session-persistence"] for claude). Pass []
                           to omit.
            json_mode_hint: appended to prompt when json_mode=True. Default
                           is a generic instruction; override for backends
                           with native JSON modes.
        """
        self.max_budget = max_budget
        self.tokens_used = 0
        self.binary = binary
        self.prompt_arg = prompt_arg
        self.model_arg = model_arg
        self.model_map = model_map or {"flash": "haiku", "strong": "sonnet"}
        self.extra_args = list(extra_args) if extra_args is not None else \
            ["--no-session-persistence"]  # claude default
        self.timeout_flash = timeout_flash
        self.timeout_strong = timeout_strong
        self.json_mode_hint = json_mode_hint or (
            "\n\nIMPORTANT FORMATTING: Reply with ONLY the raw JSON object. "
            "No markdown code fences, no prefix/suffix prose."
        )

    def _resolve_model(self, model: str) -> str:
        return self.model_map.get(model, model)

    def call(self, prompt: str, model: str = "flash", max_tokens: int = 2000,
             json_mode: bool = False) -> Tuple[str, int]:
        if self.tokens_used > self.max_budget:
            raise BudgetExceeded(
                f"Token budget exceeded before next call: "
                f"{self.tokens_used} > {self.max_budget}"
            )

        full_prompt = prompt
        if json_mode:
            full_prompt = prompt + self.json_mode_hint

        cli_model = self._resolve_model(model)
        cmd = [self.binary, *self.extra_args]
        if self.model_arg:
            cmd.extend([self.model_arg, cli_model])
        cmd.extend([self.prompt_arg, full_prompt])

        timeout = self.timeout_strong if model == "strong" else self.timeout_flash
        try:
            res = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=timeout, check=False)
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"{self.binary} CLI timed out after {timeout}s"
            ) from e
        if res.returncode != 0:
            raise RuntimeError(
                f"{self.binary} CLI exited {res.returncode}: {res.stderr[:300]}"
            )

        text = (res.stdout or "").strip()
        if json_mode:
            text = _strip_markdown_fence(text)

        approx_used = (len(prompt) + len(text)) // 4
        self.tokens_used += approx_used
        if self.tokens_used > self.max_budget:
            raise BudgetExceeded(
                f"Token budget exceeded: {self.tokens_used} > {self.max_budget}"
            )
        return text, approx_used


def _strip_markdown_fence(text: str) -> str:
    """Remove a ```json ... ``` (or ``` ... ```) wrapper if present."""
    s = text.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json|JSON)?\s*", "", s)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def relaxed_json_loads(text: str):
    """Parse JSON from an LLM response, recovering from common malformations.

    Handles:
      - Markdown code fences around the JSON
      - Smart quotes (Unicode") substituted for ASCII quotes
      - A leading or trailing prose preamble — we cut to the first `{` and
        the last `}` if strict parsing fails
      - Bare newlines inside string literals (claude-cli sonnet sometimes
        emits them; strict JSON requires them escaped) — only as a fallback.

    Returns the parsed object. Raises `json.JSONDecodeError` if recovery
    also fails; callers should treat that as a true LLM-quality failure.
    """
    s = _strip_markdown_fence(text)
    # Try strict first
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Smart quotes → ASCII (only outside of strings is ideal but we have
    # no parser; the substitution is safe enough for our 4-段-summary use).
    s2 = (s.replace("“", '"').replace("”", '"')
            .replace("‘", "'").replace("’", "'"))
    try:
        return json.loads(s2)
    except json.JSONDecodeError:
        pass

    # Trim leading/trailing prose around the outermost JSON object
    start = s2.find("{")
    end = s2.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = s2[start:end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Last-resort: escape bare newlines inside string literals.
            # Heuristic: replace LF inside any double-quoted span. We track
            # whether the previous backslash count is even (not escaped).
            buf = []
            in_str = False
            prev_backslash = False
            for ch in candidate:
                if ch == '"' and not prev_backslash:
                    in_str = not in_str
                    buf.append(ch)
                elif ch == "\n" and in_str:
                    buf.append("\\n")
                elif ch == "\r" and in_str:
                    buf.append("\\r")
                else:
                    buf.append(ch)
                prev_backslash = (ch == "\\" and not prev_backslash)
            try:
                return json.loads("".join(buf))
            except json.JSONDecodeError:
                pass

    # Give up — re-raise the strictest failure so caller sees the actual reason
    return json.loads(s)


@dataclass
class Archive:
    path: Path

    @classmethod
    def new(cls, base_dir: Path, slug: str, window_label: str,
            date_label: str, manifest: dict,
            start_date: str = None, end_date: str = None,
            include_date_label: bool = False) -> "Archive":
        """Create new archive directory + manifest.json.

        Directory layout, controlled by `include_date_label`:
          - False (default): `{slug}_{start_date}_{end_date}` when start/end
            are passed, else `{slug}-{window_label}`. The start/end form is
            self-describing — opening the folder you immediately know which
            window the archive covers.
          - True: `{slug}_{start_date}_{end_date}_run-{date_label}`, useful
            when you want to keep multiple snapshots of the same window
            taken on different days side by side.

        Existing archives at the same path are reused (no clobber), which
        is required for `Archive.resume()` to function.
        """
        if start_date and end_date:
            dir_name = f"{slug}_{start_date}_{end_date}"
            if include_date_label:
                dir_name = f"{dir_name}_run-{date_label}"
        elif include_date_label:
            dir_name = f"{slug}_{window_label}_{date_label}"
        else:
            dir_name = f"{slug}-{window_label}"
        path = Path(base_dir) / dir_name
        path.mkdir(parents=True, exist_ok=True)
        (path / "conferences").mkdir(exist_ok=True)
        manifest_full = {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "phases_completed": [],
            **manifest,
            "archive_dir": str(path),
        }
        (path / "manifest.json").write_text(
            json.dumps(manifest_full, indent=2, ensure_ascii=False)
        )
        return cls(path=path)

    @classmethod
    def resume(cls, base_dir: Path, slug: str, window_label: str,
               start_date: str = None, end_date: str = None,
               include_date_label: bool = False) -> Optional["Archive"]:
        """Open an existing archive without rewriting its manifest.

        Slug-drift tolerance: Phase 0 is LLM-driven and may produce slightly
        different keywords across runs, which changes the derived slug. So
        if an exact-slug match misses, we fall back to globbing
        `<base_dir>/*_{start_date}_{end_date}/manifest.json` and pick the
        most-recently-modified candidate. This makes `--resume` actually
        work for the same `(direction, window)` pair even when Phase 0's
        LLM output drifts.

        Returns None if no candidate is found. The caller falls back to
        `Archive.new(...)`. The dir-name formula must stay in sync with
        `Archive.new`.
        """
        base = Path(base_dir)
        candidates: List[Path] = []

        if start_date and end_date:
            exact = base / f"{slug}_{start_date}_{end_date}"
            if (exact / "manifest.json").exists():
                return cls(path=exact)
            if include_date_label:
                # date_label suffix is "today's date" at run time; we glob
                # for any run-suffix and pick the most recent.
                pattern = f"{slug}_{start_date}_{end_date}_run-*"
                candidates.extend(base.glob(pattern))
            # Slug-drift fallback: any archive in this exact window.
            candidates.extend(base.glob(f"*_{start_date}_{end_date}"))
        elif include_date_label:
            candidates.extend(base.glob(f"{slug}_{window_label}_*"))
        else:
            exact = base / f"{slug}-{window_label}"
            if (exact / "manifest.json").exists():
                return cls(path=exact)
            candidates.extend(base.glob(f"*-{window_label}"))

        # Filter to dirs that actually have a manifest, then most-recent first.
        candidates = [p for p in candidates
                      if p.is_dir() and (p / "manifest.json").exists()]
        if not candidates:
            return None
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return cls(path=candidates[0])

    def phases_done(self) -> List[str]:
        """Return phase names that have been marked done."""
        manifest = self.read_manifest()
        return [entry["phase"] for entry in manifest.get("phases_completed", [])
                if isinstance(entry, dict) and entry.get("phase")]

    def read_manifest(self) -> dict:
        return json.loads((self.path / "manifest.json").read_text())

    def write_manifest(self, manifest: dict) -> None:
        (self.path / "manifest.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False)
        )

    def mark_phase_done(self, phase: str, tokens_used: int = 0) -> None:
        manifest = self.read_manifest()
        manifest["phases_completed"].append(
            {"phase": phase, "tokens_used": tokens_used}
        )
        self.write_manifest(manifest)

    def intermediate_dir(self) -> Path:
        d = self.path / "intermediate"
        d.mkdir(exist_ok=True)
        return d

    def write_intermediate(self, name: str, data: dict) -> None:
        (self.intermediate_dir() / f"{name}.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False)
        )

    def read_intermediate(self, name: str) -> dict:
        return json.loads((self.intermediate_dir() / f"{name}.json").read_text())


import httpx
import re
from typing import List


# DBLP conf-name → URL info. Value can be:
#   - str: a single slug used for both folder and file prefix
#       e.g. "isca"  → /conf/isca/isca{year}.html
#   - tuple (folder, file_prefix): when folder ≠ file_prefix
#       e.g. ("IEEEpact", "pact") → /conf/IEEEpact/pact{year}.html
#       (DBLP separates IEEE/ACM PACT from a same-name Russian "PaCT" conference)
#       e.g. ("iwmm", "ismm") → /conf/iwmm/ismm{year}.html
#       (ISMM's DBLP folder is historical name "iwmm")
# PACMPL-series (POPL/PLDI/OOPSLA/ICFP/LCTES) do NOT have direct per-year HTML
# pages — they are indexed under journals/pacmpl/{volume}. For those, we fall
# back to the DBLP search API (see _fetch_via_dblp_search_api).
DBLP_CONF_SLUG = {
    "ISMM": ("iwmm", "ismm"),
    "PLDI": "pldi", "OOPSLA": "oopsla", "POPL": "popl",
    "ASPLOS": "asplos", "OSDI": "osdi", "SOSP": "sosp",
    "USENIX-ATC": "usenix", "ATC": "usenix",  # ATC alias; DBLP folder = file = "usenix"
    "ISCA": "isca", "MICRO": "micro", "HPCA": "hpca", "EuroSys": "eurosys",
    "FAST": "fast", "CGO": "cgo", "CC": "cc",
    "PACT": ("IEEEpact", "pact"),  # disambiguate from Russian PaCT (conf/pact)
    "SC": "sc", "PPoPP": "ppopp", "LCTES": "lctes", "ICFP": "icfp", "SAS": "sas",
}


def _resolve_slug(conf_name: str):
    """Return (folder, file_prefix) tuple regardless of mapping style."""
    raw = DBLP_CONF_SLUG.get(conf_name)
    if raw is None:
        return None
    if isinstance(raw, tuple):
        return raw
    return (raw, raw)


def _http_get(url: str, timeout: int = 30) -> str:
    """HTTP GET wrapper with custom User-Agent. Returns response body."""
    headers = {
        "User-Agent": "paper-digest/0.1 (academic research; https://github.com/anthropics/skills)"
    }
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text


def _parse_dblp_entries(html: str, conf_name: str, year: int,
                        start_idx: int = 1) -> List[dict]:
    """Extract paper records from a DBLP conference page HTML.

    DBLP entries can have nested <li> (e.g. navigation drop-downs), so we
    split the document by the entry-opening tag and treat each chunk as
    an entry. Editor entries (class="entry editor") are skipped via the
    title-presence check.
    """
    papers = []
    # Split by entry-opening tag; first chunk is everything before first entry
    chunks = re.split(r'<li class="entry[^"]*"[^>]*>', html)
    for offset, chunk in enumerate(chunks[1:]):  # skip pre-entry preamble
        idx = start_idx + offset
        title_m = re.search(r'<span class="title"[^>]*>(.*?)</span>', chunk, re.DOTALL)
        authors = re.findall(r'<span itemprop="name"[^>]*>(.*?)</span>', chunk)
        # Look for ACM DL / IEEE / DOI link first; fall back to any external link
        pdf_m = (re.search(r'href="(https?://(?:dl\.acm\.org|ieeexplore|doi\.org|www\.usenix\.org)[^"]+)"', chunk)
                 or re.search(r'href="(https?://[^"]+)"', chunk))
        if not title_m:
            continue
        papers.append({
            "id": f"C-{conf_name}-{year}-{idx:03d}",
            "source_type": "conference",
            "conference": conf_name,
            "year": year,
            "title": re.sub(r"<[^>]+>", "", title_m.group(1)).strip(),
            "authors": [re.sub(r"<[^>]+>", "", a).strip() for a in authors],
            "pdf": pdf_m.group(1) if pdf_m else "",
            "date": f"{year}-01-01",  # placeholder; refined by caller from conf metadata
        })
    return papers


def _parse_dblp_search_api(xml: str, conf_name: str, year: int) -> List[dict]:
    """Parse DBLP /search/publ/api XML into paper dicts.

    Each <hit> looks roughly like:
        <hit><info>
          <authors><author>A</author><author>B</author></authors>
          <title>The title.</title>
          <venue>ISMM</venue><year>2025</year>
          <doi>10.1145/X</doi>
          <ee>https://doi.org/10.1145/X</ee>
          <key>conf/iwmm/Foo25</key>
          <type>Conference and Workshop Papers</type>
        </info></hit>

    We skip "Editorship" entries (the proceedings front-matter).
    """
    papers: List[dict] = []
    hits = re.findall(r"<hit\s[^>]*>(.*?)</hit>", xml, re.DOTALL)
    for idx, hit in enumerate(hits, 1):
        type_m = re.search(r"<type>(.*?)</type>", hit)
        if type_m and "Editorship" in type_m.group(1):
            continue
        title_m = re.search(r"<title>(.*?)</title>", hit, re.DOTALL)
        if not title_m:
            continue
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
        # Strip trailing period DBLP appends to titles
        if title.endswith("."):
            title = title[:-1]
        authors = re.findall(r"<author[^>]*>(.*?)</author>", hit)
        doi_m = re.search(r"<doi>(.*?)</doi>", hit)
        ee_m = re.search(r"<ee>(.*?)</ee>", hit)
        pdf = ee_m.group(1) if ee_m else (f"https://doi.org/{doi_m.group(1)}" if doi_m else "")
        papers.append({
            "id": f"C-{conf_name}-{year}-{idx:03d}",
            "source_type": "conference",
            "conference": conf_name,
            "year": year,
            "title": title,
            "authors": [re.sub(r"<[^>]+>", "", a).strip() for a in authors],
            "pdf": pdf,
            "doi": doi_m.group(1) if doi_m else None,
            "date": f"{year}-01-01",
        })
    return papers


def _fetch_via_dblp_search_api(conf_name: str, year: int) -> List[dict]:
    """Universal fallback: query DBLP's search API by conference name + year.

    Works for any conference DBLP indexes, including PACMPL-series
    (POPL/PLDI/OOPSLA/ICFP/LCTES) whose papers are stored under
    journals/pacmpl/* and have no direct per-year HTML index. PACMPL
    papers carry the conference name in their <number> field (e.g.
    "OOPSLA1", "OOPSLA2", "POPL", "PLDI"), which DBLP indexes as
    searchable text — so a plain `OOPSLA year:2025` query reliably
    returns just the OOPSLA papers from PACMPL volume 9.

    We deliberately do NOT use `venue:` filter: PACMPL's `<venue>` is
    literally "Proc. ACM Program. Lang." (the journal), not the
    sub-conference name, so a venue filter would drop them all.
    """
    # h=300 fits the largest single-year PACMPL conference (OOPSLA ≈ 200).
    # ASPLOS / ISCA also fit within 300.
    url = (f"https://dblp.org/search/publ/api"
           f"?q={conf_name}+year:{year}&format=xml&h=300")
    xml = _http_get(url, timeout=30)
    papers = _parse_dblp_search_api(xml, conf_name, year)
    # PACMPL search-api returns more than just the target conference because
    # the query may match titles/abstracts too. Filter to entries whose
    # <number> field starts with the conference name (case-insensitive) for
    # PACMPL-series; pass through for non-PACMPL.
    if conf_name in {"POPL", "PLDI", "OOPSLA", "ICFP"}:
        filtered = []
        # Re-parse with <number> awareness
        hits = re.findall(r"<hit\s[^>]*>(.*?)</hit>", xml, re.DOTALL)
        for hit in hits:
            type_m = re.search(r"<type>(.*?)</type>", hit)
            if type_m and "Editorship" in type_m.group(1):
                continue
            number_m = re.search(r"<number>(.*?)</number>", hit)
            number = number_m.group(1) if number_m else ""
            if not number.upper().startswith(conf_name.upper()):
                continue
            title_m = re.search(r"<title>(.*?)</title>", hit, re.DOTALL)
            if not title_m:
                continue
            title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip().rstrip(".")
            authors = re.findall(r"<author[^>]*>(.*?)</author>", hit)
            doi_m = re.search(r"<doi>(.*?)</doi>", hit)
            ee_m = re.search(r"<ee>(.*?)</ee>", hit)
            pdf = ee_m.group(1) if ee_m else (f"https://doi.org/{doi_m.group(1)}" if doi_m else "")
            filtered.append({
                "id": f"C-{conf_name}-{year}-{len(filtered)+1:03d}",
                "source_type": "conference",
                "conference": conf_name,
                "year": year,
                "title": title,
                "authors": [re.sub(r"<[^>]+>", "", a).strip() for a in authors],
                "pdf": pdf,
                "doi": doi_m.group(1) if doi_m else None,
                "date": f"{year}-01-01",
            })
        return filtered
    return papers


def fetch_program(conf_name: str, year: int) -> List[dict]:
    """Fetch list of papers from DBLP for the given conference + year.

    Strategy:
      1. {folder}/{file_prefix}{year}.html (single volume — most conferences)
      2. {folder}/{file_prefix}{year}-1..4.html (multi-volume — ASPLOS, etc.)
      3. DBLP search API by venue+year (PACMPL-series and any conference
         whose URL template fails — universal fallback).

    Returns list of dicts: {id, title, authors[], year, pdf, doi}.
    """
    slug = _resolve_slug(conf_name)
    if slug is None:
        # No URL mapping; go straight to search API
        try:
            return _fetch_via_dblp_search_api(conf_name, year)
        except Exception:
            return []

    folder, file_prefix = slug

    # Try single-page first
    single_url = f"https://dblp.org/db/conf/{folder}/{file_prefix}{year}.html"
    try:
        html = _http_get(single_url)
        papers = _parse_dblp_entries(html, conf_name, year)
        if papers:
            return papers
        # Page existed but empty — fall through to multi-volume / search API
    except httpx.HTTPStatusError as e:
        if e.response.status_code != 404:
            raise
        # Fall through

    # Try multi-volume {file_prefix}{year}-N.html (N=1..4)
    all_papers: List[dict] = []
    for vol in range(1, 5):
        vol_url = f"https://dblp.org/db/conf/{folder}/{file_prefix}{year}-{vol}.html"
        try:
            html = _http_get(vol_url)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                break
            raise
        vol_papers = _parse_dblp_entries(html, conf_name, year,
                                         start_idx=len(all_papers) + 1)
        all_papers.extend(vol_papers)
    if all_papers:
        return all_papers

    # Last resort: DBLP search API. Critical for PACMPL series (POPL/PLDI/
    # OOPSLA/ICFP/LCTES) whose papers live under journals/pacmpl/* and have
    # no direct conference URL.
    try:
        return _fetch_via_dblp_search_api(conf_name, year)
    except Exception:
        return []

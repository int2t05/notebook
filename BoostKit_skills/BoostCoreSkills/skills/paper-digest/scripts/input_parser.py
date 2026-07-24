"""Phase 0: parse natural-language direction + time window into structured form."""
import calendar
import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Tuple, List

import dateparser

from scripts.utils import LLMClient


PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "input-parse.txt"


def _today() -> date:
    return date.today()


def parse_time_window(window_raw: str) -> Tuple[date, date]:
    """Parse natural-language time window into (start, end) dates."""
    s = window_raw.strip()

    # Explicit range YYYY-MM-DD..YYYY-MM-DD
    m = re.match(r"^(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})$", s)
    if m:
        return (date.fromisoformat(m.group(1)),
                date.fromisoformat(m.group(2)))

    # Quarter notation Q1 2026 / Q2 2025
    m = re.match(r"^Q([1-4])\s+(\d{4})$", s, re.IGNORECASE)
    if m:
        q, year = int(m.group(1)), int(m.group(2))
        start = date(year, (q - 1) * 3 + 1, 1)
        end_month = q * 3
        if end_month == 12:
            end = date(year, 12, 31)
        else:
            end = date(year, end_month + 1, 1) - timedelta(days=1)
        return (start, end)

    # "last N months/weeks/days" relative to today
    m = re.match(r"^last\s+(\d+)\s+(month|months|week|weeks|day|days)$", s, re.IGNORECASE)
    if m:
        n = int(m.group(1))
        unit = m.group(2).lower().rstrip("s")
        end = _today()
        if unit == "month":
            # Calendar-month subtraction: same day, N months earlier
            total_months = end.year * 12 + (end.month - 1) - n
            new_year, new_month = divmod(total_months, 12)
            new_month += 1
            # Clamp day to last day of target month
            last_day = calendar.monthrange(new_year, new_month)[1]
            start = date(new_year, new_month, min(end.day, last_day))
        elif unit == "week":
            start = end - timedelta(weeks=n)
        else:
            start = end - timedelta(days=n)
        return (start, end)

    # Chinese "近 N 年/月/个月/周/天" (with or without space)
    m = re.match(r"^近\s*(\d+)\s*(年|个月|月|周|天)$", s)
    if m:
        n = int(m.group(1))
        unit = m.group(2)
        end = _today()
        if unit == "年":
            # Calendar-year subtraction; clamp day for Feb 29 -> Feb 28 case
            try:
                start = end.replace(year=end.year - n)
            except ValueError:
                start = end.replace(year=end.year - n, day=end.day - 1)
        elif unit in ("个月", "月"):
            # Calendar-month subtraction: same logic as English branch
            total_months = end.year * 12 + (end.month - 1) - n
            new_year, new_month = divmod(total_months, 12)
            new_month += 1
            last_day = calendar.monthrange(new_year, new_month)[1]
            start = date(new_year, new_month, min(end.day, last_day))
        elif unit == "周":
            start = end - timedelta(weeks=n)
        else:  # 天
            start = end - timedelta(days=n)
        return (start, end)

    # Fallback: dateparser for single date
    parsed = dateparser.parse(s)
    if parsed is None:
        raise ValueError(f"Unable to parse time window: {window_raw}")
    return (parsed.date(), _today())


def generate_slug(keywords: List[str], max_words: int = 4,
                  max_chars: int = 40) -> str:
    """Generate a short filesystem-safe slug from the first few keywords.

    Defaults to 4 keywords / 40 characters so the resulting directory name
    stays readable when combined with the `_{start}_{end}` date suffix.
    Chinese characters are stripped (filesystem-safe across platforms); if
    every keyword is non-ASCII, falls back to "search".
    """
    parts: List[str] = []
    for kw in keywords[:max_words]:
        # Strip Chinese + special chars, lowercase, hyphenate words
        clean = re.sub(r"[^\w\s-]", "", kw, flags=re.UNICODE)
        # Keep only ASCII word chars (drop Chinese)
        clean = re.sub(r"[^\x00-\x7f]", "", clean)
        clean = re.sub(r"\s+", "-", clean.strip()).lower()
        if clean:
            parts.append(clean)
    return "-".join(parts)[:max_chars].rstrip("-") or "search"


def window_label(window_raw: str) -> str:
    """Short tag for archive directory naming."""
    s = window_raw.strip()
    m = re.match(r"^last\s+(\d+)\s+(month|months|week|weeks|day|days)$", s, re.IGNORECASE)
    if m:
        n, unit = m.group(1), m.group(2).lower().rstrip("s")
        return f"{n}{'mo' if unit == 'month' else unit[0]}"
    m = re.match(r"^近\s*(\d+)\s*(年|个月|月|周|天)$", s)
    if m:
        n = m.group(1)
        unit = m.group(2)
        unit_map = {"年": "y", "个月": "mo", "月": "mo", "周": "w", "天": "d"}
        return f"{n}{unit_map[unit]}"
    m = re.match(r"^Q([1-4])\s+(\d{4})$", s, re.IGNORECASE)
    if m:
        return f"Q{m.group(1)}-{m.group(2)}"
    m = re.match(r"^(\d{4})-(\d{2})-\d{2}\.\.(\d{4})-(\d{2})-\d{2}$", s)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}-{m.group(4)}"
    return re.sub(r"[^\w-]", "-", s.lower())[:20]


def parse_input(direction_raw: str, window_raw: str,
                llm: LLMClient) -> dict:
    """Full Phase 0 entry point. Returns parsed dict."""
    start, end = parse_time_window(window_raw)
    prompt = PROMPT_PATH.read_text().replace("{direction_raw}", direction_raw)
    response, _ = llm.call(prompt, model="flash", max_tokens=500, json_mode=True)
    parsed_kw = json.loads(response)
    return {
        "keywords": parsed_kw.get("keywords", []),
        "exclude": parsed_kw.get("exclude", []),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "slug": generate_slug(parsed_kw.get("keywords", [])),
        "window_label": window_label(window_raw),
    }

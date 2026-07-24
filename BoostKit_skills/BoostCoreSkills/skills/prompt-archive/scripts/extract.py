#!/usr/bin/env python3
"""prompt-archive · extract

扫描 Claude Code 顶层会话转录（*.jsonl），提取「用户真人 prompt」，关联其后的
assistant 回复做有效性统计，计算启发式特征，落机器数据集并维护增量 checkpoint。

设计契约见 docs/specs/2026-05-29-prompt-archive-design.md（§2.2 判定规则、§4 数据集
schema、§6 增量 checkpoint）。仅依赖标准库。

输出：
  <out>/dataset/sessions/<sessionId>.jsonl   每会话一份 prompt 分片
  <out>/dataset/prompts.jsonl                所有分片合并（每次运行重建）
  <out>/.archive-state.json                  增量 checkpoint
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta

# --- 噪声清洗：成对包裹块（含内容一并去除），DOTALL ---
_TAG_BLOCKS = re.compile(
    r"<command-name>.*?</command-name>"
    r"|<command-message>.*?</command-message>"
    r"|<command-args>.*?</command-args>"
    r"|<local-command-stdout>.*?</local-command-stdout>"
    r"|<local-command-caveat>.*?</local-command-caveat>"
    r"|<system-reminder>.*?</system-reminder>"
    r"|<bash-input>.*?</bash-input>"
    r"|<bash-stdout>.*?</bash-stdout>"
    r"|<bash-stderr>.*?</bash-stderr>",
    re.S,
)

# 中断信号（标记上一条 prompt 的回复被打断，本身不计入 prompt）
_INTERRUPT_MARKERS = (
    "[Request interrupted by user]",
    "[Request interrupted by user for tool use]",
)

_SLASH_ONLY = re.compile(r"^/[\w:-]+$")          # 纯斜杠命令，无正文
_SLASH_CMD_HEAD = re.compile(r"^/[A-Za-z][\w-]*(?::[\w-]+)?(?=\s|$)")  # 首词为真命令
_EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}

# 带正文的斜杠命令（如 /goal、/gitcode-pr-review）：其真实 prompt 正文存在
# <command-args> 里，必须在通用标签清洗之前抢救出来，否则会被整块删掉。
_CMD_NAME = re.compile(r"<command-name>\s*(.*?)\s*</command-name>", re.S)
_CMD_ARGS = re.compile(r"<command-args>(.*?)</command-args>", re.S)


def recover_slash_command(raw: str):
    """若 raw 是带非空 <command-args> 的斜杠命令，返回 '<命令> <正文>'；否则 None。"""
    am = _CMD_ARGS.search(raw)
    if not am:
        return None
    body = am.group(1).strip()
    if not body:
        return None
    nm = _CMD_NAME.search(raw)
    name = (nm.group(1).strip() if nm else "")
    # 偶有 args 内又重复了一遍命令名（args 以 "/goal\n..." 开头），去重
    if name and body.startswith(name):
        body = body[len(name):].lstrip()
    return (f"{name} {body}".strip() if name else body)


# ----------------------------------------------------------------------------
# 文本提取与真人 prompt 判定
# ----------------------------------------------------------------------------
def _content_to_text(content):
    """把 message.content 规整成纯文本；返回 (是否真人候选, 文本)。
    含 tool_result 的列表直接判非真人。"""
    if isinstance(content, str):
        raw = content
    elif isinstance(content, list):
        if any(isinstance(i, dict) and i.get("type") == "tool_result" for i in content):
            return False, ""
        parts = []
        for i in content:
            if not isinstance(i, dict):
                continue
            t = i.get("type")
            if t == "text":
                parts.append(i.get("text", ""))
            elif t == "image":
                parts.append("[image]")
        raw = "\n".join(parts)
    else:
        return False, ""
    return True, raw


def clean_prompt_text(raw: str) -> str:
    """去掉包裹块并 strip。"""
    return _TAG_BLOCKS.sub("", raw).strip()


def classify_user_record(rec: dict):
    """对一条 type==user 记录分类。
    返回 ('prompt', text) | ('interrupt', None) | ('noise', None)。"""
    if rec.get("isMeta"):
        return ("noise", None)
    if rec.get("isSidechain"):
        return ("noise", None)
    msg = rec.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return ("noise", None)
    ok, raw = _content_to_text(msg.get("content"))
    if not ok:
        return ("noise", None)
    stripped = raw.strip()
    # 中断标记（精确匹配整体）
    if stripped in _INTERRUPT_MARKERS:
        return ("interrupt", None)
    if stripped.startswith("<task-notification>"):
        return ("noise", None)
    # 抢救带正文的斜杠命令（/goal 等），其正文在 <command-args> 内
    recovered = recover_slash_command(raw)
    if recovered is not None:
        return ("prompt", recovered)
    text = clean_prompt_text(raw)
    if not text:
        return ("noise", None)
    # 纯斜杠命令（无正文）剔除；带正文/参数的保留
    if _SLASH_ONLY.match(text) and "\n" not in text:
        return ("noise", None)
    return ("prompt", text)


# ----------------------------------------------------------------------------
# 启发式特征
# ----------------------------------------------------------------------------
_RE_CONSTRAINT = re.compile(r"不要|必须|限制|只(?![一二三四五六七八九十])|务必|不得|一定|确保|注意|严格|禁止")
_RE_QUESTION = re.compile(r"[?？]|什么|怎么|为什么|为何|如何|是不是|是否|吗[，。\s]?$|呢[，。\s]?$|哪些|哪个")
_RE_PATH = re.compile(r"(~?/[\w./\-]+)|(\b\w+\.(py|c|h|md|sh|go|json|txt|jsonl|cc|cpp|rs|toml|yaml|yml)\b)")
_RE_CODE = re.compile(r"\b[a-z]+_[a-z_]+\b|\b[a-f0-9]{7,40}\b|`[^`]+`|\b[A-Z][a-z]+[A-Z]\w+\b")
_RE_NUMBER = re.compile(r"\d+\s*(%|ns|us|ms|x|倍|KB|MB|GB|核|线程|字节|byte)|\d+\.\d+")
_RE_BULLET = re.compile(r"(^|\n)\s*([-*]|\d+[.)、]|[一二三四五六七八九十]+[、.])", re.M)


def compute_features(text: str) -> dict:
    line_count = text.count("\n") + 1
    char_len = len(text)
    is_structured = bool(_RE_BULLET.search(text)) or text.count("；") >= 2 or line_count >= 4
    return {
        "is_question": bool(_RE_QUESTION.search(text)),
        "has_constraint_words": bool(_RE_CONSTRAINT.search(text)),
        "has_path_ref": bool(_RE_PATH.search(text)),
        "has_code_ref": bool(_RE_CODE.search(text)),
        "has_number_metric": bool(_RE_NUMBER.search(text)),
        "is_structured": is_structured,
        "is_short_followup": char_len < 20 and not is_structured,
    }


# ----------------------------------------------------------------------------
# 单会话提取
# ----------------------------------------------------------------------------
def project_label_from(cwd: str | None, project_dir: str) -> str:
    if cwd:
        base = os.path.basename(cwd.rstrip("/"))
        if base:
            return base
    # project_dir 形如 "-home-<user>-workspace-<proj>" / "-root-<proj>"；
    # 通用地剥掉 home/<user>/workspace 之类前缀，取末段作为项目名。
    name = project_dir
    m = re.match(r"^-(?:home|root|Users)-[^-]+-workspace-(.+)$", name)
    if m:
        return m.group(1)
    return name.lstrip("-")


def human_size(path: str) -> str:
    try:
        n = os.path.getsize(path)
    except OSError:
        return "?"
    size = float(n)
    for unit in ("B", "K", "M", "G", "T"):
        if size < 1024 or unit == "T":
            s = f"{size:.1f}".rstrip("0").rstrip(".")
            return f"{s}{unit}"
        size /= 1024.0
    return f"{size:.1f}T"


def extract_session(path: str):
    """解析单个会话转录，返回 (meta:dict, prompts:list[dict])。"""
    project_dir = os.path.basename(os.path.dirname(path))
    session_id = os.path.splitext(os.path.basename(path))[0]

    records = []
    custom_title = None
    ai_title = None
    git_branch = None
    cwd = None
    model = None
    line_total = 0

    with open(path, errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            line_total += 1
            try:
                o = json.loads(line)
            except json.JSONDecodeError:
                continue
            t = o.get("type")
            if t == "custom-title" and not custom_title:
                custom_title = o.get("customTitle")
            elif t == "ai-title":
                ai_title = o.get("title") or o.get("customTitle") or ai_title
            elif t in ("user", "assistant"):
                if git_branch is None:
                    git_branch = o.get("gitBranch")
                if cwd is None:
                    cwd = o.get("cwd")
                if t == "assistant" and model is None:
                    m = o.get("message")
                    if isinstance(m, dict):
                        model = m.get("model")
                records.append(o)

    # 顺序遍历：真人 prompt 之后、下一条真人 prompt 之前的 assistant 归属于它
    prompts = []
    active = None  # 当前 prompt 的响应累加器

    def flush(active):
        if active is not None:
            prompts.append(active)

    for o in records:
        t = o.get("type")
        if t == "user":
            kind, text = classify_user_record(o)
            if kind == "prompt":
                flush(active)
                feats = compute_features(text)
                active = {
                    "session_id": session_id,
                    "project": project_dir,
                    "project_label": project_label_from(cwd, project_dir),
                    "git_branch": git_branch,
                    "seq": len(prompts) + 1,
                    "timestamp": o.get("timestamp"),
                    "text": text,
                    "char_len": len(text),
                    "line_count": text.count("\n") + 1,
                    # 仅当首词是真正的斜杠命令（/word 或 /a:b）才标记；
                    # 以绝对路径 /home/... 开头的 prompt 不算命令。
                    "has_slash_command": bool(_SLASH_CMD_HEAD.match(text)),
                    "slash_command": (_SLASH_CMD_HEAD.match(text).group(0)
                                      if _SLASH_CMD_HEAD.match(text) else None),
                    "features": feats,
                    "response": {
                        "assistant_turns": 0,
                        "output_tokens": 0,
                        "tool_calls": 0,
                        "tool_names": [],
                        "files_edited": 0,
                        "interrupted": False,
                        "stop_reason": None,
                    },
                    "quality_score": None,
                }
            elif kind == "interrupt":
                if active is not None:
                    active["response"]["interrupted"] = True
            # noise / tool_result：忽略
        elif t == "assistant" and active is not None:
            m = o.get("message")
            if not isinstance(m, dict):
                continue
            resp = active["response"]
            resp["assistant_turns"] += 1
            usage = m.get("usage") or {}
            resp["output_tokens"] += int(usage.get("output_tokens") or 0)
            sr = m.get("stop_reason")
            if sr:
                resp["stop_reason"] = sr
            for item in (m.get("content") or []):
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    resp["tool_calls"] += 1
                    name = item.get("name")
                    if name:
                        resp["tool_names"].append(name)
                        if name in _EDIT_TOOLS:
                            resp["files_edited"] += 1

    flush(active)

    # tool_names 去重保序
    for p in prompts:
        seen = []
        for n in p["response"]["tool_names"]:
            if n not in seen:
                seen.append(n)
        p["response"]["tool_names"] = seen
        p["session_key"] = f"{project_dir}__{session_id}"
        p["prompt_id"] = f"{project_dir}__{session_id}#{p['seq']}"

    ts = [p["timestamp"] for p in prompts if p.get("timestamp")]
    date_start = min(ts)[:10] if ts else None
    date_end = max(ts)[:10] if ts else None
    title = custom_title or ai_title
    if not title and prompts:
        first = prompts[0]["text"].strip().splitlines()[0]
        title = (first[:40] + "…") if len(first) > 40 else first
    if not title:
        title = session_id[:8]

    meta = {
        "session_id": session_id,
        "key": f"{project_dir}__{session_id}",
        "project": project_dir,
        "project_label": project_label_from(cwd, project_dir),
        "git_branch": git_branch,
        "title": title,
        "title_source": "custom" if custom_title else ("ai" if ai_title else "first-prompt"),
        "model": model,
        "date_start": date_start,
        "date_end": date_end,
        "prompt_count": len(prompts),
        "transcript_lines": line_total,
        "transcript_size": human_size(path),
        "transcript_path": path,
        "mtime": os.path.getmtime(path),
    }
    return meta, prompts


# ----------------------------------------------------------------------------
# 增量编排
# ----------------------------------------------------------------------------
def load_state(out_dir: str) -> dict:
    p = os.path.join(out_dir, ".archive-state.json")
    if os.path.exists(p):
        try:
            with open(p) as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {"sessions": {}}


def now_iso_local() -> str:
    # 固定 +08:00（项目在 CST 环境），避免依赖被禁用的 Date.now 之类
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).replace(microsecond=0).isoformat()


def run(projects_root: str, out_dir: str, force: bool = False) -> dict:
    os.makedirs(os.path.join(out_dir, "dataset", "sessions"), exist_ok=True)
    state = load_state(out_dir)
    sessions_state = state.get("sessions", {})

    files = sorted(glob.glob(os.path.join(projects_root, "*", "*.jsonl")))
    # 排除 subagents 子目录（glob 已限定两层，天然排除 */subagents/*）

    added, updated, skipped = [], [], []
    all_meta = []

    for path in files:
        session_id = os.path.splitext(os.path.basename(path))[0]
        project_dir = os.path.basename(os.path.dirname(path))
        key = f"{project_dir}__{session_id}"  # 复合键：隔离跨 worktree 同 session_id
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            continue
        # 快速行数（用于增量判断）
        try:
            with open(path, "rb") as fh:
                lines = sum(1 for _ in fh)
        except OSError:
            continue

        prev = sessions_state.get(key)
        shard = os.path.join(out_dir, "dataset", "sessions", f"{key}.jsonl")
        meta_path = os.path.join(out_dir, "dataset", "sessions", f"{key}.meta.json")
        unchanged = (
            prev
            and abs(prev.get("mtime", -1) - mtime) < 1e-6
            and prev.get("lines") == lines
            and os.path.exists(shard)
            and os.path.exists(meta_path)
        )
        if unchanged and not force:
            skipped.append(key)
            with open(meta_path) as fh:
                all_meta.append(json.load(fh))
            continue

        meta, prompts = extract_session(path)
        meta["lines"] = lines
        with open(shard, "w") as fh:
            for p in prompts:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")
        with open(meta_path, "w") as fh:
            json.dump(meta, fh, ensure_ascii=False)
        all_meta.append(meta)
        sessions_state[key] = {
            "session_id": session_id,
            "project": project_dir,
            "path": path,
            "mtime": mtime,
            "lines": lines,
            "prompts": meta["prompt_count"],
            "md": None,  # 由 render 填
        }
        (updated if prev else added).append(key)

    # 合并所有分片为 prompts.jsonl（按复合键去重，避免跨 worktree 同 session_id 重复计入）
    combined = os.path.join(out_dir, "dataset", "prompts.jsonl")
    total_prompts = 0
    dates = []
    seen_keys = set()
    with open(combined, "w") as out:
        for meta in sorted(all_meta, key=lambda m: (m.get("date_start") or "", m.get("key") or m["session_id"])):
            mkey = meta.get("key") or f"{meta['project']}__{meta['session_id']}"
            if mkey in seen_keys:
                continue
            seen_keys.add(mkey)
            shard = os.path.join(out_dir, "dataset", "sessions", f"{mkey}.jsonl")
            if not os.path.exists(shard):
                continue
            with open(shard) as fh:
                for line in fh:
                    if line.strip():
                        out.write(line)
                        total_prompts += 1
            if meta.get("date_start"):
                dates.append(meta["date_start"])
            if meta.get("date_end"):
                dates.append(meta["date_end"])

    state["sessions"] = sessions_state
    state["last_run"] = now_iso_local()
    state["data_range"] = {"min": min(dates) if dates else None, "max": max(dates) if dates else None}
    state["totals"] = {"sessions": len(seen_keys), "prompts": total_prompts}
    with open(os.path.join(out_dir, ".archive-state.json"), "w") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)

    summary = {
        "added": added,
        "updated": updated,
        "skipped": skipped,
        "sessions": len(all_meta),
        "prompts": total_prompts,
        "data_range": state["data_range"],
        "last_run": state["last_run"],
    }
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="提取 Claude 会话中的真人 prompt 到数据集")
    ap.add_argument("--projects-root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--out", default=os.path.expanduser("~/workspace/prompt-archive"))
    ap.add_argument("--force", action="store_true", help="忽略 checkpoint，全量重抽")
    args = ap.parse_args(argv)

    summary = run(args.projects_root, args.out, force=args.force)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(
        f"\n[extract] 会话={summary['sessions']} prompt={summary['prompts']} "
        f"新增={len(summary['added'])} 更新={len(summary['updated'])} 跳过={len(summary['skipped'])} "
        f"范围={summary['data_range']['min']}→{summary['data_range']['max']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

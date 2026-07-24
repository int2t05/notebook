#!/usr/bin/env python3
"""prompt-archive · render

由 extract 产出的数据集渲染人类可读归档：
  <out>/sessions/<date>_<label>_<slug>_<sid8>.md   每会话一份
  <out>/INDEX.md                                    主索引（处理截止时间+分组表+分析报告区）

读取 <out>/dataset/sessions/*.meta.json 与 *.jsonl 分片，以及 .archive-state.json。
仅依赖标准库。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import unicodedata

# 项目分组：决定 INDEX 里的小标题归类
GROUP_RULES = [
    ("jemalloc 系列", lambda lbl: lbl.startswith("jemalloc") or lbl in ("malloc-bench", "kqmalloc")),
    ("Go / 其它内存", lambda lbl: lbl in ("golang-mem", "goservicesopt", "prefix", "gcc")),
    ("工具 / Skill 元项目", lambda lbl: lbl in ("skills", "magazine-skills", "make-money")),
]


def group_of(label: str) -> str:
    for name, pred in GROUP_RULES:
        if pred(label):
            return name
    return "其它"


def slugify(text: str, maxlen: int = 40) -> str:
    """生成文件名友好的 slug：保留中文、字母数字，其余转连字符。"""
    text = text.strip()
    out = []
    for ch in text:
        cat = unicodedata.category(ch)
        if ch.isalnum() or cat.startswith("L"):  # 字母（含 CJK）或数字
            out.append(ch)
        elif ch in " \t-_/":
            out.append("-")
    s = "".join(out)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:maxlen] or "untitled"


def hhmm(ts: str | None) -> str:
    if not ts or "T" not in ts:
        return "??:??"
    return ts[11:16]


def hms(ts: str | None) -> str:
    if not ts or "T" not in ts:
        return "??:??:??"
    return ts[11:19]


def load_dataset(out_dir: str):
    """返回 {session_id: (meta, [prompts...])}。"""
    ds_dir = os.path.join(out_dir, "dataset", "sessions")
    data = {}
    for meta_path in sorted(glob.glob(os.path.join(ds_dir, "*.meta.json"))):
        with open(meta_path) as fh:
            meta = json.load(fh)
        key = meta.get("key") or f"{meta.get('project')}__{meta['session_id']}"
        shard = os.path.join(ds_dir, f"{key}.jsonl")
        prompts = []
        if os.path.exists(shard):
            with open(shard) as fh:
                for line in fh:
                    if line.strip():
                        prompts.append(json.loads(line))
        prompts.sort(key=lambda p: (p.get("timestamp") or "", p.get("seq", 0)))
        data[key] = (meta, prompts)
    return data


def md_filename(meta: dict) -> str:
    date = meta.get("date_start") or "0000-00-00"
    label = slugify(meta.get("project_label") or "proj", 24)
    slug = slugify(meta.get("title") or "session", 32)
    sid8 = meta["session_id"][:8]
    return f"{date}_{label}_{slug}_{sid8}.md"


def render_session_md(meta: dict, prompts: list) -> str:
    fm = [
        "---",
        f"session_id: {meta['session_id']}",
        f"project: {meta.get('project_label')}",
        f"title: {json.dumps(meta.get('title'), ensure_ascii=False)}",
        f"git_branch: {meta.get('git_branch')}",
        f"date_start: {meta.get('date_start')}",
        f"date_end: {meta.get('date_end')}",
        f"prompt_count: {meta.get('prompt_count')}",
        f"transcript_lines: {meta.get('transcript_lines')}",
        f"transcript_size: {meta.get('transcript_size')}",
        f"transcript_path: {meta.get('transcript_path')}",
        f"model: {meta.get('model')}",
        f"title_source: {meta.get('title_source')}",
        "---",
        "",
    ]
    title = meta.get("title") or meta["session_id"][:8]
    span = ""
    if prompts:
        span = f"{hhmm(prompts[0].get('timestamp'))}–{hhmm(prompts[-1].get('timestamp'))}"
    head = (
        f"# {title}\n\n"
        f"> 会话 `{meta['session_id'][:8]}` · {meta.get('project_label')} · "
        f"{meta.get('date_start')} · {meta.get('prompt_count')} 条 prompt · {span}\n>\n"
        f"> 转录源文件：`{meta.get('transcript_path')}`\n"
    )
    body = []
    for p in prompts:
        ts = hms(p.get("timestamp"))
        text = p.get("text", "").rstrip()
        resp = p.get("response", {})
        badge_bits = []
        if resp.get("tool_calls"):
            badge_bits.append(f"🔧{resp['tool_calls']}")
        if resp.get("files_edited"):
            badge_bits.append(f"✏️{resp['files_edited']}")
        if resp.get("output_tokens"):
            badge_bits.append(f"↩{resp['output_tokens']}tok")
        if resp.get("interrupted"):
            badge_bits.append("⛔中断")
        badge = ("  `" + " ".join(badge_bits) + "`") if badge_bits else ""
        # 标题用纯 token `p{seq}`：Obsidian 按标题文本、GitHub/VS Code 按 slug 都能用 #p{seq}
        # 命中（HTML <a id> 锚点 Obsidian 不识别）。时间/徽章放标题下一行。
        seq = p.get("seq")
        subtitle = f"**第 {seq} 条 · [{ts}]**{badge}".rstrip()
        body.append(f"## p{seq}\n{subtitle}\n\n{text}\n")
    return "\n".join(fm) + head + "\n" + "\n".join(body) + "\n"


def render_index(out_dir: str, data: dict, state: dict, run_summary: dict | None) -> str:
    metas = [m for (m, _) in data.values()]
    total_sessions = len(metas)
    total_prompts = sum(m.get("prompt_count", 0) for m in metas)
    rng = state.get("data_range", {}) or {}
    last_run = state.get("last_run", "?")

    lines = ["# Prompt 归档索引", ""]
    lines.append(f"- **处理截止时间**：{last_run}")
    lines.append(f"- **数据时间范围**：{rng.get('min')} → {rng.get('max')}")
    lines.append(f"- **会话总数**：{total_sessions} ｜ **prompt 总数**：{total_prompts}")
    if run_summary:
        lines.append(
            f"- **本次运行**：新增 {len(run_summary.get('added', []))} / "
            f"更新 {len(run_summary.get('updated', []))} / "
            f"跳过 {len(run_summary.get('skipped', []))}"
        )
    lines.append("")
    lines.append("> 后续重跑可从「处理截止时间」继续：未变更的会话会被自动跳过。")
    lines.append("")

    # 分析报告区
    lines.append("## 分析报告")
    reports = sorted(glob.glob(os.path.join(out_dir, "analysis", "*.md")))
    if reports:
        for r in reports:
            rel = os.path.relpath(r, out_dir)
            name = os.path.splitext(os.path.basename(r))[0]
            lines.append(f"- [{name}]({rel})")
    else:
        lines.append("- （尚未生成，运行 `analyze` 后出现）")
    lines.append("")

    # 项目维度小结
    by_label = {}
    for m in metas:
        lbl = m.get("project_label") or "?"
        d = by_label.setdefault(lbl, {"sessions": 0, "prompts": 0})
        d["sessions"] += 1
        d["prompts"] += m.get("prompt_count", 0)
    lines.append("## 项目概览")
    lines.append("")
    lines.append("| 项目 | 会话数 | prompt 数 |")
    lines.append("|------|-------|----------|")
    for lbl in sorted(by_label, key=lambda k: -by_label[k]["prompts"]):
        d = by_label[lbl]
        lines.append(f"| {lbl} | {d['sessions']} | {d['prompts']} |")
    lines.append("")

    # 会话列表：分组 + 按日期倒序
    lines.append("## 会话列表（按日期倒序）")
    lines.append("")
    groups = {}
    for m in metas:
        groups.setdefault(group_of(m.get("project_label") or ""), []).append(m)
    group_order = [n for (n, _) in GROUP_RULES] + ["其它"]
    for gname in group_order:
        gmetas = groups.get(gname)
        if not gmetas:
            continue
        lines.append(f"### {gname}")
        lines.append("")
        lines.append("| 日期 | 项目 | 标题 | prompt数 | 转录大小 | 时间段 | 链接 |")
        lines.append("|------|------|------|---------|---------|--------|------|")
        for m in sorted(gmetas, key=lambda x: (x.get("date_start") or "", x["session_id"]), reverse=True):
            mkey = m.get("key") or f"{m.get('project')}__{m['session_id']}"
            _, prompts = data[mkey]
            span = ""
            if prompts:
                span = f"{hhmm(prompts[0].get('timestamp'))}–{hhmm(prompts[-1].get('timestamp'))}"
            mdname = m.get("md") or md_filename(m)
            title = (m.get("title") or "").replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {m.get('date_start')} | {m.get('project_label')} | {title} | "
                f"{m.get('prompt_count')} | {m.get('transcript_size')} | {span} | "
                f"[md](sessions/{mdname}) |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def run(out_dir: str, run_summary: dict | None = None) -> dict:
    os.makedirs(os.path.join(out_dir, "sessions"), exist_ok=True)
    data = load_dataset(out_dir)

    # 状态（用于回填 md 路径 + 取 last_run/range）
    state_path = os.path.join(out_dir, ".archive-state.json")
    state = {}
    if os.path.exists(state_path):
        with open(state_path) as fh:
            state = json.load(fh)
    sessions_state = state.get("sessions", {})

    written = 0
    used_names = set()
    for key, (meta, prompts) in data.items():
        mdname = md_filename(meta)
        if mdname in used_names:  # 跨 worktree 同 session_id 防文件名碰撞
            base, ext = os.path.splitext(mdname)
            mdname = f"{base}_{slugify(meta.get('project',''),12)}{ext}"
        used_names.add(mdname)
        meta["md"] = mdname
        path = os.path.join(out_dir, "sessions", mdname)
        with open(path, "w") as fh:
            fh.write(render_session_md(meta, prompts))
        # 回写 md 字段到 meta.json，令数据集自含
        meta_path = os.path.join(out_dir, "dataset", "sessions", f"{key}.meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "w") as fh:
                json.dump(meta, fh, ensure_ascii=False)
        written += 1
        if key in sessions_state:
            sessions_state[key]["md"] = mdname

    index = render_index(out_dir, data, state, run_summary)
    with open(os.path.join(out_dir, "INDEX.md"), "w") as fh:
        fh.write(index)

    if state:
        state["sessions"] = sessions_state
        with open(state_path, "w") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)

    return {"sessions_md": written, "index": os.path.join(out_dir, "INDEX.md")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="把 prompt 数据集渲染为 md 归档与 INDEX")
    ap.add_argument("--out", default=os.path.expanduser("~/workspace/prompt-archive"))
    args = ap.parse_args(argv)
    res = run(args.out)
    print(f"[render] 写出 {res['sessions_md']} 个会话 md，索引：{res['index']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

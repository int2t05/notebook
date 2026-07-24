#!/usr/bin/env python3
"""prompt-archive · analyze

对数据集做全量启发式质量打分，回写 quality_score，产出量化报告与 LLM 深析选样。

打分维度（各 0–1，加权求和）：
  length      0.15  长度适配（过短/超长无结构扣分）
  structure   0.30  结构性（分点 / 约束词 / 多行）
  context     0.30  上下文充分（路径 / 代码符号 / 数值指标）
  effect      0.25  有效性代理（回复 token / 工具调用 / 文件编辑 / 是否中断）

输出：
  回写 <out>/dataset/sessions/*.jsonl 与 prompts.jsonl 的 quality_score / score_components
  <out>/analysis/<date>-prompt-quality-heuristic.md   量化报告
  <out>/analysis/_sample.json                         供 LLM 深析的选样
仅依赖标准库。
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from collections import defaultdict

# 复用 render 的 md 文件名规则，让榜单链接指向真实的会话 md 文件
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render  # noqa: E402

W = {"length": 0.15, "structure": 0.30, "context": 0.30, "effect": 0.25}


def build_md_map(out_dir: str) -> dict:
    """session_key -> 会话 md 文件名（优先 meta 里 render 回写的，缺失则按规则推算）。"""
    md_map = {}
    ds_dir = os.path.join(out_dir, "dataset", "sessions")
    for meta_path in glob.glob(os.path.join(ds_dir, "*.meta.json")):
        try:
            meta = json.load(open(meta_path))
        except (json.JSONDecodeError, OSError):
            continue
        key = meta.get("key") or f"{meta.get('project')}__{meta.get('session_id')}"
        md_map[key] = meta.get("md") or render.md_filename(meta)
    return md_map


def loc_link(p: dict, md_map: dict) -> str:
    """生成指向 sessions/<md>#p<seq> 的相对跳转链接（报告在 analysis/ 下）。"""
    md = md_map.get(p.get("session_key"))
    seq = p.get("seq")
    if not md or seq is None:
        return "—"
    sid8 = (p.get("session_id") or "")[:8]
    return f"[{sid8}#{seq}](../sessions/{md}#p{seq})"


def _length_score(char_len: int, is_structured: bool) -> float:
    cl = char_len
    if cl < 15:
        return 0.15
    if cl < 40:
        return 0.45
    if cl <= 600:
        return 1.0
    if cl <= 1500:
        return 0.85
    if cl <= 4000:
        return 0.65 if is_structured else 0.5
    return 0.5 if is_structured else 0.35


def _structure_score(f: dict, line_count: int) -> float:
    s = 0.0
    if f.get("is_structured"):
        s += 0.5
    if f.get("has_constraint_words"):
        s += 0.3
    if line_count >= 3:
        s += 0.2
    return min(1.0, s)


def _context_score(f: dict) -> float:
    bits = [f.get("has_path_ref"), f.get("has_code_ref"), f.get("has_number_metric")]
    return sum(1 for b in bits if b) / 3.0


def _effect_score(resp: dict) -> float:
    ot = resp.get("output_tokens") or 0
    ot_score = min(1.0, math.log10(ot + 1) / 4.0)  # 1e4 tok → 1.0
    tool_score = min(1.0, (resp.get("tool_calls") or 0) / 8.0)
    edit_bonus = min(0.3, (resp.get("files_edited") or 0) * 0.1)
    eff = min(1.0, 0.5 * ot_score + 0.4 * tool_score + edit_bonus)
    if resp.get("interrupted"):
        eff *= 0.6
    return eff


def score_prompt(p: dict) -> dict:
    f = p.get("features", {})
    comp = {
        "length": round(_length_score(p.get("char_len", 0), f.get("is_structured", False)), 3),
        "structure": round(_structure_score(f, p.get("line_count", 1)), 3),
        "context": round(_context_score(f), 3),
        "effect": round(_effect_score(p.get("response", {})), 3),
    }
    total = sum(W[k] * comp[k] for k in W)
    return {"quality_score": round(total, 4), "score_components": comp}


def iso_week(date_str: str | None) -> str:
    if not date_str:
        return "?"
    try:
        import datetime as _dt
        y, m, d = map(int, date_str.split("-"))
        iso = _dt.date(y, m, d).isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    except Exception:
        return "?"


def load_all(out_dir: str):
    ds_dir = os.path.join(out_dir, "dataset", "sessions")
    shards = {}
    for shard in sorted(glob.glob(os.path.join(ds_dir, "*.jsonl"))):
        sid = os.path.splitext(os.path.basename(shard))[0]
        rows = []
        with open(shard) as fh:
            for line in fh:
                if line.strip():
                    rows.append(json.loads(line))
        shards[shard] = rows
    return shards


def run(out_dir: str, date_tag: str, top_k: int = 30, bottom_k: int = 30) -> dict:
    os.makedirs(os.path.join(out_dir, "analysis"), exist_ok=True)
    md_map = build_md_map(out_dir)
    shards = load_all(out_dir)

    all_rows = []
    for shard, rows in shards.items():
        for p in rows:
            sc = score_prompt(p)
            p["quality_score"] = sc["quality_score"]
            p["score_components"] = sc["score_components"]
            all_rows.append(p)
        with open(shard, "w") as fh:
            for p in rows:
                fh.write(json.dumps(p, ensure_ascii=False) + "\n")

    # 重建合并 prompts.jsonl（带分数）
    combined = os.path.join(out_dir, "dataset", "prompts.jsonl")
    with open(combined, "w") as out:
        for p in sorted(all_rows, key=lambda x: (x.get("timestamp") or "", x.get("prompt_id") or "")):
            out.write(json.dumps(p, ensure_ascii=False) + "\n")

    n = len(all_rows)
    if n == 0:
        raise SystemExit("数据集为空，请先运行 extract")

    # --- 统计 ---
    scores = sorted(p["quality_score"] for p in all_rows)
    mean = sum(scores) / n
    median = scores[n // 2]
    buckets = defaultdict(int)
    for s in scores:
        buckets[min(9, int(s * 10))] += 1

    by_proj = defaultdict(list)
    by_week = defaultdict(list)
    for p in all_rows:
        by_proj[p.get("project_label", "?")].append(p["quality_score"])
        by_week[iso_week((p.get("timestamp") or "")[:10])].append(p["quality_score"])

    feat_keys = ["is_question", "has_constraint_words", "has_path_ref", "has_code_ref",
                 "has_number_metric", "is_structured", "is_short_followup"]
    feat_prev = {k: sum(1 for p in all_rows if p.get("features", {}).get(k)) for k in feat_keys}

    # 非平凡集合（排除短澄清/极短）用于排行与选样
    nontrivial = [p for p in all_rows
                  if not p.get("features", {}).get("is_short_followup")
                  and p.get("char_len", 0) >= 15]
    ranked = sorted(nontrivial, key=lambda p: p["quality_score"], reverse=True)
    top = ranked[:top_k]
    bottom = list(reversed(ranked[-bottom_k:])) if len(ranked) >= bottom_k else []

    # 分层代表：每项目最高分 + 每周中位样本
    strat = {}
    best_per_proj = {}
    for p in nontrivial:
        lbl = p.get("project_label", "?")
        if lbl not in best_per_proj or p["quality_score"] > best_per_proj[lbl]["quality_score"]:
            best_per_proj[lbl] = p
    for p in best_per_proj.values():
        strat[p["prompt_id"]] = p
    week_groups = defaultdict(list)
    for p in nontrivial:
        week_groups[iso_week((p.get("timestamp") or "")[:10])].append(p)
    for wk, ps in week_groups.items():
        ps.sort(key=lambda x: x["quality_score"])
        strat[ps[len(ps) // 2]["prompt_id"]] = ps[len(ps) // 2]

    # 选样合并去重
    sample = {}
    for p in top:
        sample[p["prompt_id"]] = {**p, "_bucket": "top"}
    for p in bottom:
        sample.setdefault(p["prompt_id"], {**p, "_bucket": "bottom"})
    for pid, p in strat.items():
        sample.setdefault(pid, {**p, "_bucket": "stratified"})
    sample_list = list(sample.values())

    sample_path = os.path.join(out_dir, "analysis", "_sample.json")
    with open(sample_path, "w") as fh:
        json.dump(sample_list, fh, ensure_ascii=False, indent=2)

    # --- 量化报告 ---
    def trunc(s, n=70):
        s = s.replace("\n", " ").strip()
        return (s[:n] + "…") if len(s) > n else s

    L = []
    L.append(f"# Prompt 质量量化报告（启发式）— {date_tag}")
    L.append("")
    L.append(f"- prompt 总数：**{n}**")
    L.append(f"- 质量分：均值 **{mean:.3f}** ｜ 中位 **{median:.3f}** ｜ 最低 {scores[0]:.3f} ｜ 最高 {scores[-1]:.3f}")
    L.append(f"- 短澄清/极短占比：{feat_prev['is_short_followup']}/{n} = {feat_prev['is_short_followup']/n*100:.0f}%")
    L.append("")
    L.append("> 打分维度权重：length 0.15 / structure 0.30 / context 0.30 / effect 0.25。"
             "短澄清与极短 prompt 不参与排行与 LLM 选样（依赖上文，不宜独立评判）。")
    L.append("")

    L.append("## 分数分布")
    L.append("")
    L.append("| 区间 | 数量 | 占比 |")
    L.append("|------|------|------|")
    for b in range(10):
        cnt = buckets.get(b, 0)
        bar = "█" * round(cnt / max(1, max(buckets.values())) * 24)
        L.append(f"| {b/10:.1f}–{(b+1)/10:.1f} | {cnt} | {bar} {cnt/n*100:.0f}% |")
    L.append("")

    L.append("## 按项目平均分")
    L.append("")
    L.append("| 项目 | prompt 数 | 平均分 |")
    L.append("|------|----------|--------|")
    for lbl in sorted(by_proj, key=lambda k: -sum(by_proj[k]) / len(by_proj[k])):
        arr = by_proj[lbl]
        L.append(f"| {lbl} | {len(arr)} | {sum(arr)/len(arr):.3f} |")
    L.append("")

    L.append("## 按周趋势")
    L.append("")
    L.append("| 周 | prompt 数 | 平均分 |")
    L.append("|----|----------|--------|")
    for wk in sorted(by_week):
        if wk == "?":
            continue
        arr = by_week[wk]
        L.append(f"| {wk} | {len(arr)} | {sum(arr)/len(arr):.3f} |")
    L.append("")

    L.append("## 特征出现率")
    L.append("")
    L.append("| 特征 | 命中 | 占比 |")
    L.append("|------|------|------|")
    name_map = {
        "is_question": "提问句", "has_constraint_words": "含约束词",
        "has_path_ref": "给了路径", "has_code_ref": "含代码符号",
        "has_number_metric": "含数值指标", "is_structured": "结构化",
        "is_short_followup": "短澄清",
    }
    for k in feat_keys:
        L.append(f"| {name_map[k]} | {feat_prev[k]} | {feat_prev[k]/n*100:.0f}% |")
    L.append("")

    L.append(f"## Top {len(top)} 高分 prompt")
    L.append("")
    L.append("> 「位置」列点击可跳转到该 prompt 在会话 md 中的章节。")
    L.append("")
    L.append("| # | 分 | 项目 | 日期 | 位置 | prompt |")
    L.append("|---|----|------|------|------|--------|")
    for i, p in enumerate(top, 1):
        L.append(f"| {i} | {p['quality_score']:.3f} | {p.get('project_label')} | "
                 f"{(p.get('timestamp') or '')[:10]} | {loc_link(p, md_map)} | {trunc(p.get('text',''))} |")
    L.append("")

    L.append(f"## Bottom {len(bottom)} 低分 prompt（非短澄清）")
    L.append("")
    L.append("> 「位置」列点击可跳转到该 prompt 在会话 md 中的章节。")
    L.append("")
    L.append("| # | 分 | 项目 | 日期 | 位置 | prompt |")
    L.append("|---|----|------|------|------|--------|")
    for i, p in enumerate(bottom, 1):
        L.append(f"| {i} | {p['quality_score']:.3f} | {p.get('project_label')} | "
                 f"{(p.get('timestamp') or '')[:10]} | {loc_link(p, md_map)} | {trunc(p.get('text',''))} |")
    L.append("")
    L.append(f"---\n\n选样供 LLM 深析：`analysis/_sample.json`（{len(sample_list)} 条）。"
             f"最佳实践报告由 Workflow 生成于同目录。")
    L.append("")

    report_path = os.path.join(out_dir, "analysis", f"{date_tag}-prompt-quality-heuristic.md")
    with open(report_path, "w") as fh:
        fh.write("\n".join(L))

    return {
        "prompts": n,
        "mean": mean,
        "median": median,
        "report": report_path,
        "sample": sample_path,
        "sample_count": len(sample_list),
        "top": [{"id": p["prompt_id"], "score": p["quality_score"]} for p in top],
        "bottom": [{"id": p["prompt_id"], "score": p["quality_score"]} for p in bottom],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="prompt 质量启发式打分与选样")
    ap.add_argument("--out", default=os.path.expanduser("~/workspace/prompt-archive"))
    ap.add_argument("--date", default=None, help="报告日期标签 YYYY-MM-DD（默认从 state 取）")
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--bottom", type=int, default=30)
    args = ap.parse_args(argv)

    date_tag = args.date
    if not date_tag:
        sp = os.path.join(args.out, ".archive-state.json")
        if os.path.exists(sp):
            with open(sp) as fh:
                st = json.load(fh)
            date_tag = (st.get("last_run") or "0000-00-00")[:10]
        else:
            date_tag = "report"

    res = run(args.out, date_tag, top_k=args.top, bottom_k=args.bottom)
    print(json.dumps({k: v for k, v in res.items() if k not in ("top", "bottom")},
                     ensure_ascii=False, indent=2))
    print(f"[analyze] {res['prompts']} 条，均值 {res['mean']:.3f}，"
          f"报告 {res['report']}，选样 {res['sample_count']} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

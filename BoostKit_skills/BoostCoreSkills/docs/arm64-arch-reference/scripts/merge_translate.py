#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""汇总翻译 Workflow 产出的 skill_build/desc/out_*.json，生成两个数据模块：

  feat_desc.py   DESC[name] = 中文介绍（特性）
  instr_desc.py  INSTR_DESC[iform_id] = 中文一行简介（指令）

并对照源数据报告覆盖率与缺失项。缺失项不阻断（生成器会回退英文）。
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, 'skill_build', 'desc')


def load_outs(prefix):
    merged = {}
    for p in sorted(glob.glob(os.path.join(DESC, f'out_{prefix}_*.json'))):
        try:
            d = json.load(open(p, encoding='utf-8'))
        except Exception as e:
            sys.stderr.write(f"[警告] 跳过损坏文件 {os.path.basename(p)}: {e}\n")
            continue
        for k, v in d.items():
            if isinstance(v, str) and v.strip():
                merged[k] = v.strip()
    return merged


def write_module(path, varname, mapping, ordered_keys, doc):
    """按 ordered_keys 顺序写出确定性的 Python 数据模块（repr 保证转义正确）。"""
    lines = ['# -*- coding: utf-8 -*-', f'"""{doc}"""', '', f'{varname} = {{']
    for k in ordered_keys:
        if k in mapping:
            lines.append(f'    {k!r}: {mapping[k]!r},')
    # 收尾：源数据外的多余键（理论上不该有，保险起见也写入）
    extra = [k for k in mapping if k not in set(ordered_keys)]
    for k in sorted(extra):
        lines.append(f'    {k!r}: {mapping[k]!r},')
    lines.append('}')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def main():
    # 源数据顺序与全集
    from gen_feat_table import extract
    _, rows = extract()
    feat_names = [r['name'] for r in rows]

    from gen_instr_table import collect
    _, cats, _ = collect()
    instr_ids = [r['id'] for cat in cats for r in cats[cat]]

    feat_map = load_outs('feat')
    instr_map = load_outs('instr')

    # 安全护栏：若 skill_build/desc/ 下没有任何 out_*.json（例如中间件已被清理），
    # 不要用空字典覆盖已固化的 feat_desc.py / instr_desc.py。需重译时先跑 prep_translate.py。
    if not feat_map and not instr_map:
        sys.stderr.write("[中止] 未找到任何 out_*.json 翻译中间件；为避免清空 feat_desc.py/instr_desc.py，"
                         "本次不写入。如需重新翻译，请先运行 prep_translate.py 并执行翻译 Workflow。\n")
        sys.exit(1)

    write_module(os.path.join(HERE, 'feat_desc.py'), 'DESC', feat_map, feat_names,
                 'FEAT_XXX 的中文功能介绍（由翻译 Workflow 生成，merge_translate.py 汇总）。')
    write_module(os.path.join(HERE, 'instr_desc.py'), 'INSTR_DESC', instr_map, instr_ids,
                 'A64 指令的中文一行简介，键为 iform id（由翻译 Workflow 生成，merge_translate.py 汇总）。')

    # 覆盖率报告
    fmiss = [n for n in feat_names if n not in feat_map]
    imiss = [i for i in instr_ids if i not in instr_map]
    sys.stderr.write(f"feat DESC 覆盖={len(feat_names)-len(fmiss)}/{len(feat_names)}\n")
    if fmiss:
        sys.stderr.write(f"  feat 缺失({len(fmiss)}): {', '.join(fmiss[:20])}{' …' if len(fmiss)>20 else ''}\n")
    sys.stderr.write(f"instr INSTR_DESC 覆盖={len(instr_ids)-len(imiss)}/{len(instr_ids)}\n")
    if imiss:
        sys.stderr.write(f"  instr 缺失({len(imiss)}): {', '.join(imiss[:20])}{' …' if len(imiss)>20 else ''}\n")
    sys.stderr.write("已写入 feat_desc.py, instr_desc.py\n")


if __name__ == '__main__':
    main()

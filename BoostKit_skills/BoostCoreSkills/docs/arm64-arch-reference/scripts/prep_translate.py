#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""准备翻译批次输入文件，供翻译 Workflow 使用。

输出到 skill_build/desc/：
  in_feat_NNN.json   每个含若干 {name, title, before, after}
  in_instr_NNN.json  每个含若干 {id, heading, brief}
  manifest.json      列出所有批次文件路径与计数（供 Workflow args 使用）

翻译 agent 读取 in_*.json，产出 out_*.json（{key: 中文}），再由 merge_translate.py 汇总。
"""
import os, json, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DESC = os.path.join(HERE, 'skill_build', 'desc')

FEAT_BATCH  = 40
INSTR_BATCH = 120


def chunk(lst, n):
    return [lst[i:i+n] for i in range(0, len(lst), n)]


def main():
    os.makedirs(DESC, exist_ok=True)

    # --- Features ---
    from gen_feat_table import extract
    _, rows = extract()
    feat_items = [{'name': r['name'], 'title': r['title'],
                   'before': r['desc_en'], 'after': r['after_en']} for r in rows]

    # --- Instructions ---
    from gen_instr_table import collect
    _, cats, _ = collect()
    instr_items = []
    for cat in cats:
        for r in cats[cat]:
            instr_items.append({'id': r['id'], 'heading': r['heading'], 'brief': r['brief']})

    manifest = {'feat': [], 'instr': []}

    for i, b in enumerate(chunk(feat_items, FEAT_BATCH)):
        p = os.path.join(DESC, f'in_feat_{i:03d}.json')
        json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        manifest['feat'].append({'in': p, 'out': os.path.join(DESC, f'out_feat_{i:03d}.json'),
                                 'n': len(b)})

    for i, b in enumerate(chunk(instr_items, INSTR_BATCH)):
        p = os.path.join(DESC, f'in_instr_{i:03d}.json')
        json.dump(b, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        manifest['instr'].append({'in': p, 'out': os.path.join(DESC, f'out_instr_{i:03d}.json'),
                                  'n': len(b)})

    json.dump(manifest, open(os.path.join(DESC, 'manifest.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    sys.stderr.write(f"feat: {len(feat_items)} 项 / {len(manifest['feat'])} 批\n")
    sys.stderr.write(f"instr: {len(instr_items)} 项 / {len(manifest['instr'])} 批\n")
    sys.stderr.write(f"已写入 {DESC}/manifest.json\n")


if __name__ == '__main__':
    main()

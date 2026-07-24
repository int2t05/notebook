#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 Features.json 提取全部 FEAT_XXX 特性，合并翻译/归类字典，生成 FEAT_列表.md。"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'Features.json')

# 源数据官方下载地址（skill 自包含：产物只引用下载地址，不依赖本地路径）
FEATURES_URL = ('https://developer.arm.com/-/cdn-downloads/permalink/'
                'Exploration-Tools-Arm-Architecture-Features/AARCHMRS/'
                'AARCHMRS_A_profile-2026-03_96.tar.gz')

def flat(v):
    if v is None: return []
    if isinstance(v, str): return [v]
    if isinstance(v, list):
        o = []
        for i in v: o.extend(flat(i))
        return o
    return [str(v)]

def extract():
    d = json.load(open(SRC, encoding='utf-8'))
    meta = d['_meta']['version']
    feats = [x for x in d['parameters'] if x['name'].startswith('FEAT_')]
    rows = []
    for x in feats:
        after = flat(x['description'].get('after'))
        before = flat(x['description'].get('before'))
        txt = ' '.join(after + before)
        m = re.search(r'from Armv(\d+\.\d+)', txt)
        ver = ('Armv' + m.group(1)) if m else '—'
        if 'AArch64 state only' in txt: state = 'AArch64'
        elif 'AArch32 state only' in txt: state = 'AArch32'
        elif 'both AArch64 and AArch32' in txt: state = 'AArch64+AArch32'
        else: state = '—'
        # 可选/强制：区分三态。注意先判「可选+后转强制」，避免被 is OPTIONAL 短路掩盖
        m_mand = re.search(r'mandatory from Armv(\d+\.\d+)', txt)
        if 'is OPTIONAL' in txt and m_mand:
            opt = f'可选（Armv{m_mand.group(1)} 起强制）'        # 可选→强制
        elif 'is OPTIONAL' in txt and re.search(r'\bmandatory\b', txt, re.I):
            opt = '可选（后续版本起强制）'                        # 有 mandatory 但无版本号
        elif 'is OPTIONAL' in txt:
            opt = '可选'                                         # 纯可选
        elif re.search(r'\bmandatory\b', txt, re.I):
            opt = '强制'                                         # 纯强制
        else:
            opt = '可选'   # 兜底（实测不触发）
        rows.append({'name': x['name'], 'title': x['title'],
                     'ver': ver, 'state': state, 'opt': opt,
                     'desc_en': ' '.join(before).strip(),
                     'after_en': ' '.join(after).strip()})
    rows.sort(key=lambda r: r['name'])
    return meta, rows

def ver_key(v):
    """把 'Armv9.6' / '—' 转成可排序的 (major, minor) 元组。未知版本排最后。"""
    m = re.match(r'Armv(\d+)\.(\d+)', v)
    return (int(m.group(1)), int(m.group(2))) if m else (99, 99)

def cell(s):
    """清洗表格单元格：折叠空白、转义管道符。"""
    return re.sub(r'\s+', ' ', s or '').replace('|', r'\|').strip()

def build_md():
    from feat_meta import META, GROUP_ORDER
    try:
        from feat_desc import DESC
    except ImportError:
        DESC = {}   # 中文介绍尚未生成时回退英文 before 文本
    meta, rows = extract()

    # 校验 META 覆盖
    names = {r['name'] for r in rows}
    missing = sorted(names - set(META))
    extra = sorted(set(META) - names)
    if missing or extra:
        sys.stderr.write(f"[错误] META 未覆盖: {missing}\n[错误] META 多余: {extra}\n")
        sys.exit(1)

    # 合并 META + DESC，分组
    desc_hit = 0
    groups = {g: [] for g in GROUP_ORDER}
    for r in rows:
        zh, grp = META[r['name']]
        r['zh'] = zh
        d = DESC.get(r['name'])
        if d:
            desc_hit += 1
        r['desc'] = d or r['desc_en']   # 缺中文介绍则回退英文 before 文本
        groups[grp].append(r)
    for g in groups:
        groups[g].sort(key=lambda r: (ver_key(r['ver']), r['name']))

    v = meta
    out = []
    out.append("# ARM A-profile 架构特性（FEAT_XXX）一览表\n")
    out.append("> 本表由 ARM 官方机器可读规范（AARCHMRS A-profile）自动生成，逐条人工翻译并按功能域归类。")
    out.append(f"> 源数据下载：{FEATURES_URL}\n")
    out.append("| 项目 | 值 |")
    out.append("| --- | --- |")
    out.append(f"| 架构版本 | {v['architecture']} |")
    out.append(f"| 发布 ref | {v['ref']} |")
    out.append(f"| schema 版本 | {v['schema']} |")
    out.append(f"| build | {v['build']} |")
    out.append(f"| 数据时间戳 | {v['timestamp']} |")
    out.append(f"| FEAT 特性总数 | {len(rows)} |")
    out.append("")
    out.append("**列说明**：")
    out.append("- **特性名**：官方规范中的 `FEAT_*` 特性标识符。")
    out.append("- **英文标题 / 中文翻译**：官方 `title` 原文及中文译文（专有名词如 SVE、PMU、ASID、ZA 等保留英文）。")
    out.append("- **中文介绍**：依据官方描述（`description.before`）撰写的中文功能简介；缺译时回退英文原文。")
    out.append("- **引入版本**：从特性描述中解析的 “OPTIONAL from ArmvX.Y”；`—` 表示描述未注明。")
    out.append("- **执行状态**：AArch64 / AArch32 / AArch64+AArch32；`—` 表示描述未注明。")
    out.append("- **可选/强制**：`可选` / `可选（ArmvX 起强制）` / `强制` 三态；多数特性为可选扩展，部分在更高架构版本起转为强制。")
    out.append("")
    # 目录（锚点遵循 GitHub 规则：小写、去除非字母数字/空格/连字符、空格转连字符）
    def slug(s):
        s = s.lower()
        s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
        return s.strip().replace(' ', '-')
    out.append("## 目录\n")
    for g in GROUP_ORDER:
        out.append(f"- [{g}](#{slug(g)})（{len(groups[g])} 项）")
    out.append("")

    for g in GROUP_ORDER:
        rs = groups[g]
        out.append(f"## {g}\n")
        out.append(f"共 {len(rs)} 项。\n")
        out.append("| 特性名 | 英文标题 | 中文翻译 | 中文介绍 | 引入版本 | 执行状态 | 可选/强制 |")
        out.append("| --- | --- | --- | --- | --- | --- | --- |")
        for r in rs:
            out.append(f"| `{r['name']}` | {cell(r['title'])} | {cell(r['zh'])} | "
                       f"{cell(r['desc'])} | {r['ver']} | {r['state']} | {r['opt']} |")
        out.append("")

    return '\n'.join(out) + '\n', rows, missing, desc_hit

if __name__ == '__main__':
    meta, rows = extract()
    miss = sum(1 for r in rows if r['ver'] == '—')
    sys.stderr.write(f"FEAT 数={len(rows)}  版本未命中={miss}\n")
    if '--dump' in sys.argv:
        for r in rows:
            print(f"{r['name']}\t{r['ver']}\t{r['state']}\t{r['opt']}\t{r['title']}")
    else:
        md, rows, missing, desc_hit = build_md()
        sys.stderr.write(f"META 覆盖={len(rows) - len(missing)}/{len(rows)}  "
                         f"DESC 覆盖={desc_hit}/{len(rows)}"
                         + ("（其余回退英文 before）\n" if desc_hit < len(rows) else "\n"))
        # 同时写到仓库根目录（向后兼容）与 skill 参考目录
        targets = [
            os.path.join(HERE, 'FEAT_列表.md'),
            os.path.join(HERE, 'skill_build', 'reference', 'Features.md'),
        ]
        for outpath in targets:
            os.makedirs(os.path.dirname(outpath), exist_ok=True)
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(md)
            sys.stderr.write(f"已写入 {outpath}\n")

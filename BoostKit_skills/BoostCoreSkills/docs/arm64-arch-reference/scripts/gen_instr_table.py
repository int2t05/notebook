#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""解析 A64 指令 XML（2026-03_rel 快照），按功能分类生成 instructions 参考 Markdown。

数据源：Instructions/ISA_A64_xml_.../ISA_A64_xml_..._2026-03_rel/ 下的
  - 4 个索引文件：index.xml(Base) / fpsimdindex.xml(SIMD&FP) / sveindex.xml(SVE) / mortlachindex.xml(SME)
  - 每个 <iform> 指向的单指令 XML（抽取助记符 / instr-class / 汇编模板 / 关联 FEAT_*）

产物（默认写到 skill_build/reference/instructions/ 下）：
  base.md  simd-fp.md  sve.md  sme.md  +  00-index.md（分类索引）

中文一行简介取自 instr_meta.INSTR_DESC（按 iform id），缺失则回退英文 brief 并打印覆盖率。

无第三方依赖，纯标准库（xml.etree, glob, re, sys, os）。
"""
import os, re, sys, glob
import xml.etree.ElementTree as ET

from instr_meta import CATEGORY_LABELS, INDEX_TO_CATEGORY
try:
    from instr_desc import INSTR_DESC   # 由 merge_translate.py 生成
except ImportError:
    INSTR_DESC = {}                     # 中文简介尚未生成时回退英文 brief

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, 'skill_build', 'reference', 'instructions')

# 源数据官方下载地址（skill 自包含：产物只引用下载地址，不依赖本地路径）
INSTR_URL = ('https://developer.arm.com/-/cdn-downloads/permalink/'
             'Exploration-Tools-A64-ISA/ISA_A64/'
             'ISA_A64_xml_A_profile-2026-03_96.tar.gz')


def find_a64_dir():
    """定位 A64 的 2026-03_rel 指令快照目录。"""
    pat = os.path.join(HERE, 'Instructions', 'ISA_A64_xml_*', 'ISA_A64_xml_*2026-03_rel')
    hits = sorted(glob.glob(pat))
    if not hits:
        sys.stderr.write(f"[错误] 找不到 A64 指令快照目录：{pat}\n")
        sys.exit(1)
    return hits[-1]


def asm_text(asm):
    """把 <asmtemplate> 子树还原成单行汇编模板文本。"""
    return re.sub(r'\s+', ' ', ''.join(asm.itertext())).strip()


def parse_iform(path):
    """从单指令 XML 抽取 (mnemonic, instr_class, [asmtemplates], [FEAT_*])。"""
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        sys.stderr.write(f"[警告] 解析失败 {os.path.basename(path)}: {e}\n")
        return None
    mn = root.find(".//docvars/docvar[@key='mnemonic']")
    ic = root.find(".//docvars/docvar[@key='instr-class']")
    asms = []
    for a in root.findall('.//encoding/asmtemplate'):
        t = asm_text(a)
        if t and t not in asms:
            asms.append(t)
    feats = sorted({m for av in root.findall('.//arch_variant')
                    for m in re.findall(r'FEAT_\w+', av.get('feature', ''))})
    return {
        'mnemonic': mn.get('value') if mn is not None else '',
        'iclass':   ic.get('value') if ic is not None else '',
        'asms':     asms,
        'feats':    feats,
    }


def collect():
    """遍历 4 个索引，合并单指令信息，返回 {category: [row, ...]}。"""
    a64 = find_a64_dir()
    cats = {k: [] for k in CATEGORY_LABELS}
    total = 0
    for stem, cat in INDEX_TO_CATEGORY.items():
        idx_path = os.path.join(a64, stem + '.xml')
        root = ET.parse(idx_path).getroot()
        for iform in root.findall('.//iform'):
            iid     = iform.get('id')
            heading = (iform.get('heading') or '').strip()
            brief   = (iform.text or '').strip().rstrip('.')
            ifile   = iform.get('iformfile')
            info    = parse_iform(os.path.join(a64, ifile)) or {}
            cats[cat].append({
                'id':       iid,
                'heading':  heading,
                'brief':    brief,
                'mnemonic': info.get('mnemonic', ''),
                'asms':     info.get('asms', []),
                'feats':    info.get('feats', []),
            })
            total += 1
    for cat in cats:
        cats[cat].sort(key=lambda r: (r['heading'].lower(), r['id']))
    return a64, cats, total


def md_cell(s):
    """转义 Markdown 表格单元格中的管道符。"""
    return s.replace('|', r'\|')


def asm_cell(asms, cap=16):
    """把多条汇编模板拼成表格单元格：每条 inline code，<br> 分隔。

    cap 取 16（实测全量 A64 指令的最大编码数为 15），即默认不截断、保证速查表自包含；
    若未来数据升级出现超量指令，超出部分折叠并注明总数，提示回源 XML。"""
    if not asms:
        return '—'
    shown = [f'`{md_cell(a)}`' for a in asms[:cap]]
    if len(asms) > cap:
        shown.append(f'…（共 {len(asms)} 种编码）')
    return '<br>'.join(shown)


def slug(s):
    s = s.lower()
    s = re.sub(r'[^\w\s-]', '', s, flags=re.UNICODE)
    return s.strip().replace(' ', '-')


def write_md(a64, cats, total):
    os.makedirs(OUT, exist_ok=True)
    desc_hit = 0
    desc_total = 0

    # 各分类文件
    for cat, (label, fname) in CATEGORY_LABELS.items():
        rows = cats[cat]
        out = []
        out.append(f"# A64 指令 — {label}\n")
        out.append(f"> 数据源：ARM 官方 A64 ISA 机器可读规范（2026-03_rel），共 {len(rows)} 条。"
                   f"汇编模板列即官方 `asmtemplate`（Encoding）。")
        out.append(f"> 源数据下载：{INSTR_URL}\n")
        out.append("| 指令名 | 英文简述 | 中文简介 | 汇编模板（Encoding） | 关联特性 |")
        out.append("| --- | --- | --- | --- | --- |")
        for r in rows:
            desc_total += 1
            zh = INSTR_DESC.get(r['id'])
            if zh:
                desc_hit += 1
            else:
                zh = r['brief']  # 回退英文 brief
            feats = ', '.join(r['feats']) if r['feats'] else '—'
            out.append(f"| `{md_cell(r['heading'])}` | {md_cell(r['brief'])} | "
                       f"{md_cell(zh)} | {asm_cell(r['asms'])} | {md_cell(feats)} |")
        out.append("")
        with open(os.path.join(OUT, fname), 'w', encoding='utf-8') as f:
            f.write('\n'.join(out) + '\n')

    # 分类索引
    idx = []
    idx.append("# A64 指令分类索引\n")
    idx.append(f"> 数据源：ARM 官方 A64 ISA 机器可读规范（2026-03_rel），A64 指令共 {total} 条，按功能分 4 类。")
    idx.append(f"> 源数据下载：{INSTR_URL}\n")
    idx.append("| 分类 | 文件 | 指令数 |")
    idx.append("| --- | --- | --- |")
    for cat, (label, fname) in CATEGORY_LABELS.items():
        idx.append(f"| {label} | [{fname}](./{fname}) | {len(cats[cat])} |")
    idx.append("")
    with open(os.path.join(OUT, '00-index.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(idx) + '\n')

    return desc_hit, desc_total


if __name__ == '__main__':
    a64, cats, total = collect()
    sys.stderr.write(f"A64 指令总数={total}  "
                     + "  ".join(f"{k}={len(cats[k])}" for k in CATEGORY_LABELS) + "\n")
    if '--dump' in sys.argv:
        for cat in CATEGORY_LABELS:
            for r in cats[cat]:
                print(f"{cat}\t{r['id']}\t{r['heading']}\t{r['brief']}")
    else:
        hit, tot = write_md(a64, cats, total)
        sys.stderr.write(f"INSTR_DESC 覆盖={hit}/{tot}"
                         + ("（其余回退英文 brief）\n" if hit < tot else "\n"))
        sys.stderr.write(f"已写入 {OUT}/（base/simd-fp/sve/sme + 00-index）\n")

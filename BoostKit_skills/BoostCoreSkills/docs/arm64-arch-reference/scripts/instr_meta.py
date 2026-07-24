# -*- coding: utf-8 -*-
"""A64 指令分类配置（供 gen_instr_table.py 使用）。

中文一行简介（INSTR_DESC[iform_id]）在独立的 instr_desc.py 中，由 merge_translate.py 生成；
键为指令 XML 的 iform id（如 "ADD_addsub_imm"），全局唯一，避免助记符重名冲突。

CATEGORY_LABELS 把 4 个索引文件对应的顶层分类映射为中文章节名。
"""

# 顶层分类：键 = 索引文件 stem，值 = (中文显示名, 输出文件名)
CATEGORY_LABELS = {
    "base":    ("基础指令（Base）", "base.md"),
    "simd-fp": ("SIMD 与浮点指令（SIMD & Floating-point）", "simd-fp.md"),
    "sve":     ("SVE 可伸缩向量指令", "sve.md"),
    "sme":     ("SME 可伸缩矩阵指令", "sme.md"),
}

# 索引文件 stem -> 分类键
INDEX_TO_CATEGORY = {
    "index":         "base",
    "fpsimdindex":   "simd-fp",
    "sveindex":      "sve",
    "mortlachindex": "sme",
}

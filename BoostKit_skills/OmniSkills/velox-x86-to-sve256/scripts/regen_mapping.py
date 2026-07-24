#!/usr/bin/env python3
"""
Generate AVX2 to SVE migration mapping table.
Maps each AVX2 intrinsic to its SVE equivalent.

Data sources:
- AVX2: Intel Intrinsics Guide (data-latest.xml)
- SVE: ARM Developer (arm_intrinsics.json)
"""

import xml.etree.ElementTree as ET
import json
import os
import re
from collections import defaultdict
from datetime import datetime

SCRIPT_DIR = os.path.dirname(__file__)
REF_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "references"))
XML_PATH = os.path.join(REF_DIR, "intel_intrinsics.xml")
JSON_PATH = os.path.join(REF_DIR, "arm_intrinsics.json")
OUTPUT_FILE = os.path.join(REF_DIR, "avx2_to_sve.md")

AVX2_ETYPES = {
    "INT8": "int8", "INT16": "int16", "INT32": "int32", "INT64": "int64",
    "FP32": "float32", "FP64": "float64",
    "UI8": "uint8", "UI16": "uint16", "UI32": "uint32", "UI64": "uint64",
}

SVE_TYPE_MAP = {
    "int8": ["s8", "int8"],
    "int16": ["s16", "int16"],
    "int32": ["s32", "int32"],
    "int64": ["s64", "int64"],
    "uint8": ["u8", "uint8"],
    "uint16": ["u16", "uint16"],
    "uint32": ["u32", "uint32"],
    "uint64": ["u64", "uint64"],
    "float32": ["f32", "float32", "float"],
    "float64": ["f64", "float64", "double"],
}

OPERATION_KEYWORDS = {
    "add": ["add"],
    "sub": ["sub"],
    "mul": ["mul"],
    "div": ["div"],
    "and": ["and"],
    "or": ["or"],
    "xor": ["xor", "eor"],
    "not": ["not", "neg"],
    "shl": ["shl", "shift_left", "lsl"],
    "shr": ["shr", "shift_right", "lsr"],
    "cmp": ["cmp", "compare", "cmpeq", "cmpgt", "cmplt", "cmpge", "cmple", "cmpne"],
    "load": ["ld", "load"],
    "store": ["st", "store"],
    "set": ["set", "dup"],
    "shuffle": ["shuffle", "permute", "ext", "zip", "uzp", "trn"],
    "abs": ["abs"],
    "min": ["min"],
    "max": ["max"],
    "sqrt": ["sqrt"],
    "rsqrt": ["rsqrt", "rsqrte"],
    "recip": ["recip", "recpe"],
    "fma": ["fma", "mla", "mad"],
    "convert": ["cvt", "convert", "cast"],
    "blend": ["blend", "merge", "sel"],
    "unpack": ["unpack", "uzp"],
    "pack": ["pack"],
    "sll": ["sll", "shift_left_logical"],
    "srl": ["srl", "shift_right_logical"],
    "sra": ["sra", "shift_right_arithmetic", "asr"],
    "broadcast": ["dup", "broadcast"],
    "gather": ["ld1", "gather"],
    "reduce": ["reduce", "addv", "minv", "maxv"],
    "sad": ["sad", "sadalp"],
    "madd": ["mla", "mad"],
    "msub": ["mls", "msub"],
    "dot": ["dot", "dotprod"],
}


def parse_avx2_intrinsics(xml_path):
    """Parse AVX2 intrinsics from Intel XML."""
    print(f"[parse] Loading AVX2 from {xml_path} ...")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    result = []

    for intr in root.iter("intrinsic"):
        cpuid_list = [c.text.strip() for c in intr.findall("CPUID") if c.text]
        if "AVX2" not in cpuid_list:
            continue

        name = intr.get("name", "")

        ret_el = intr.find("return")
        ret_type = ret_el.get("type", "") if ret_el is not None else ""
        ret_etype = ret_el.get("etype", "") if ret_el is not None else ""

        params = []
        for p in intr.findall("parameter"):
            params.append({
                "type": p.get("type", ""),
                "varname": p.get("varname", ""),
                "etype": p.get("etype", ""),
            })

        cat_el = intr.find("category")
        category = cat_el.text.strip() if cat_el is not None and cat_el.text else ""

        desc_el = intr.find("description")
        description = desc_el.text.strip() if desc_el is not None and desc_el.text else ""

        op_el = intr.find("operation")
        operation = op_el.text.strip() if op_el is not None and op_el.text else ""

        instructions = []
        for ins in intr.findall("instruction"):
            iname = ins.get("name", "")
            instructions.append(iname)

        result.append({
            "name": name,
            "category": category,
            "ret_type": ret_type,
            "ret_etype": ret_etype,
            "params": params,
            "description": description,
            "operation": operation,
            "instructions": instructions,
        })

    result.sort(key=lambda x: (x["category"], x["name"]))
    print(f"[parse] AVX2 intrinsics: {len(result)}")
    return result


def parse_sve_intrinsics(json_path):
    """Parse SVE/SVE2 intrinsics from ARM JSON."""
    print(f"[parse] Loading SVE from {json_path} ...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    target_isas = {"SVE", "SVE2"}
    exclude_isas = {"Neon", "Helium"}

    for intr in data:
        simd_isa_list = intr.get("SIMD_ISA", [])
        if not isinstance(simd_isa_list, list):
            simd_isa_list = [simd_isa_list]

        has_target = any(isa in target_isas for isa in simd_isa_list)
        has_exclude = any(isa in exclude_isas for isa in simd_isa_list)
        if not has_target or has_exclude:
            continue

        name = intr.get("name", "")
        name_clean = name.replace("[__arm_]", "").replace("[", "").replace("]", "")
        name_clean = re.sub(r"_x\d+$", "", name_clean)

        ret_type_info = intr.get("return_type", {})
        if isinstance(ret_type_info, dict):
            ret_type = ret_type_info.get("value", "")
        else:
            ret_type = str(ret_type_info) if ret_type_info else ""

        ret_etype = ""
        if ret_type.startswith("sv"):
            for t, keywords in SVE_TYPE_MAP.items():
                if any(k in ret_type.lower() for k in keywords):
                    ret_etype = t
                    break

        params = []
        for p in intr.get("arguments", []):
            if isinstance(p, str):
                parts = p.rsplit(" ", 1)
                if len(parts) == 2:
                    ptype, pname = parts
                else:
                    ptype, pname = p, ""
                param_etype = ""
                if ptype.startswith("sv"):
                    for t, keywords in SVE_TYPE_MAP.items():
                        if any(k in ptype.lower() for k in keywords):
                            param_etype = t
                            break
                params.append({
                    "type": ptype,
                    "name": pname,
                    "etype": param_etype,
                })

        category = intr.get("instruction_group", "")
        if category:
            parts = category.split("|")
            category = parts[0] if parts else category

        description = intr.get("description", "")

        result.append({
            "name": name,
            "name_clean": name_clean,
            "category": category,
            "ret_type": ret_type,
            "ret_etype": ret_etype,
            "params": params,
            "description": description,
            "simd_isa": ", ".join(simd_isa_list),
        })

    print(f"[parse] SVE intrinsics: {len(result)}")
    return result


def detect_operation_type(name, description, operation):
    """Detect the operation type from intrinsic name and description."""
    name_lower = name.lower()
    desc_lower = description.lower() if description else ""
    op_lower = operation.lower() if operation else ""

    combined = f"{name_lower} {desc_lower} {op_lower}"

    for op_type, keywords in OPERATION_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                return op_type

    return "other"


def detect_element_type(etype, ret_etype, params):
    """Detect the primary element type."""
    if etype:
        return AVX2_ETYPES.get(etype, etype.lower())

    if ret_etype:
        return AVX2_ETYPES.get(ret_etype, ret_etype.lower())

    for p in params:
        if p.get("etype"):
            return AVX2_ETYPES.get(p["etype"], p["etype"].lower())

    return "unknown"


def find_sve_equivalent(avx2_intr, sve_intrinsics):
    """Find SVE intrinsics that match the AVX2 operation."""
    op_type = detect_operation_type(
        avx2_intr["name"],
        avx2_intr["description"],
        avx2_intr["operation"]
    )

    elem_type = detect_element_type(
        None,
        avx2_intr["ret_etype"],
        avx2_intr["params"]
    )

    matches = []

    for sve_intr in sve_intrinsics:
        sve_name = sve_intr["name_clean"].lower()

        if op_type == "other":
            continue

        keywords = OPERATION_KEYWORDS.get(op_type, [])
        keyword_match = any(kw in sve_name for kw in keywords)

        if not keyword_match:
            continue

        type_match = False
        if elem_type == "unknown":
            type_match = True
        else:
            sve_keywords = SVE_TYPE_MAP.get(elem_type, [])
            sve_ret_type = sve_intr["ret_type"].lower()
            sve_etype = sve_intr["ret_etype"].lower() if sve_intr["ret_etype"] else ""

            if any(k in sve_ret_type for k in sve_keywords) or sve_etype == elem_type:
                type_match = True

        if keyword_match and type_match:
            matches.append(sve_intr)

    return matches[:5]


def generate_migration_table(avx2_intrinsics, sve_intrinsics):
    """Generate the migration mapping table."""
    print("[gen] Building migration table ...")

    lines = []

    lines.append("# AVX2 → SVE Migration Reference\n")
    lines.append(f"> **生成日期**: {datetime.now().strftime('%Y-%m-%d')}  \n")
    lines.append(f"> **用途**: x86 AVX2（256-bit）到 ARM SVE/SVE2 迁移对照表\n\n")
    lines.append("---\n\n")

    lines.append("## 概述\n\n")
    lines.append(
        "本文档提供 x86 AVX2 intrinsics 到 ARM SVE/SVE2 的迁移映射。"
        "AVX2 是 256-bit 固定长度 SIMD，而 SVE 是可伸缩向量扩展（128-2048 bit）。"
        "在迁移时，SVE 的向量长度（VL）可配置为 256-bit 以匹配 AVX2 的处理宽度。\n\n"
    )
    lines.append(
        "**关键差异**:\n"
        "- AVX2 使用固定 256-bit 寄存器（`__m256i`, `__m256`, `__m256d`）\n"
        "- SVE 使用可变长度寄存器（`svint32_t`, `svfloat32_t` 等），需要谓词寄存器（`svbool_t`）控制活跃元素\n"
        "- SVE 指令通常需要额外的谓词参数（`pg`）来指定活跃元素\n"
        "- SVE 使用 `svptrue_b32()` 等函数创建全活跃谓词\n\n"
    )
    lines.append("---\n\n")

    cats = defaultdict(list)
    for intr in avx2_intrinsics:
        cats[intr["category"]].append(intr)

    lines.append("## 目录\n\n")
    for cat in sorted(cats.keys()):
        anchor = cat.lower().replace(" ", "-").replace("/", "")
        lines.append(f"- [{cat}](#{anchor})\n")
    lines.append("\n---\n\n")

    for cat in sorted(cats.keys()):
        lines.append(f"## {cat}\n\n")

        for avx2_intr in cats[cat]:
            lines.append(f"### `{avx2_intr['name']}`\n\n")

            sig = f"{avx2_intr['ret_type']} {avx2_intr['name']}("
            if avx2_intr["params"]:
                sig += ", ".join(f"{p['type']} {p['varname']}" for p in avx2_intr["params"])
            else:
                sig += "void"
            sig += ")"
            lines.append(f"**AVX2 签名**: `{sig}`\n\n")

            elem_type = detect_element_type(None, avx2_intr["ret_etype"], avx2_intr["params"])
            op_type = detect_operation_type(avx2_intr["name"], avx2_intr["description"], avx2_intr["operation"])

            if avx2_intr["instructions"]:
                lines.append(f"**x86 指令**: `{', '.join(avx2_intr['instructions'])}`\n\n")

            if avx2_intr["description"]:
                lines.append(f"**描述**: {avx2_intr['description']}\n\n")

            matches = find_sve_equivalent(avx2_intr, sve_intrinsics)

            if matches:
                lines.append("**SVE 对应指令**:\n\n")
                for i, sve_intr in enumerate(matches, 1):
                    sve_name = sve_intr["name"]
                    sve_sig = f"{sve_intr['ret_type']} {sve_name}("
                    if sve_intr["params"]:
                        sve_sig += ", ".join(f"{p['type']} {p['name']}" for p in sve_intr["params"])
                    else:
                        sve_sig += "void"
                    sve_sig += ")"
                    lines.append(f"{i}. `{sve_sig}` — {sve_intr['simd_isa']}\n")
                lines.append("\n")

                lines.append("**迁移示例** (假设 VL=256-bit):\n")
                lines.append("```c\n")
                lines.append(f"// AVX2: {avx2_intr['name']}\n")

                var_names = [p['varname'] for p in avx2_intr["params"]]
                if matches:
                    sve_match = matches[0]
                    param_names = [p['name'] for p in sve_match["params"]]
                    if param_names and param_names[0] in ["pg", "pred", "p"]:
                        predicate = "svptrue_b32()" if "float" in elem_type or elem_type == "int32" else "svptrue_b8()"
                        call_args = [predicate] + var_names[:len(param_names)-1]
                    else:
                        call_args = var_names[:len(param_names)]
                    lines.append(f"// SVE: {sve_match['name']}({', '.join(call_args)})\n")
                lines.append("```\n\n")
            else:
                lines.append("**SVE 对应**: 未找到直接映射，可能需要组合多条指令或使用 NEON\n\n")

            lines.append("---\n\n")

    return "".join(lines)


def main():
    avx2_intrinsics = parse_avx2_intrinsics(XML_PATH)
    sve_intrinsics = parse_sve_intrinsics(JSON_PATH)

    doc = generate_migration_table(avx2_intrinsics, sve_intrinsics)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(doc)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"[write] {OUTPUT_FILE} ({len(avx2_intrinsics)} AVX2 -> SVE mappings, {size_kb:.1f} KB)")
    print("\nDone. Migration reference generated.")


if __name__ == "__main__":
    main()
#!/bin/bash
# 归一化对比 native 输出 vs vanilla 输出
# native (WRITE_TO_FILE):  +I,v1,v2,...   (逗号分隔)
# vanilla (print sink .out): +I[v1, v2, ...] (方括号, 逗号空格)
# 归一化为 v1|v2|v3 排序后 diff
# 用法: bash compare.sh <native_file> <vanilla_file>
NATIVE=${1:-/tmp/flink_output.txt}
VANILLA=${2:-/tmp/vanilla_out.txt}

normalize() {
    # native 写 SQL NULL 为大写 "NULL", vanilla print 为小写 "null"; 语义相等, 归一化统一小写
    sed -E \
        -e 's/^\+I\[/+I,/' \
        -e 's/\]$//' \
        -e 's/^[+-]I,//' \
        -e 's/, /,/g' \
        -e 's/\bNULL\b/null/g' \
        "$1" \
    | sed -E 's/,/|/g' \
    | sort
}

echo "=== native  : $NATIVE ($(wc -l < "$NATIVE" 2>/dev/null) rows) ==="
echo "=== vanilla : $VANILLA ($(wc -l < "$VANILLA" 2>/dev/null) rows) ==="

normalize "$NATIVE"  > /tmp/_native_norm.txt
normalize "$VANILLA" > /tmp/_vanilla_norm.txt

if diff -u /tmp/_native_norm.txt /tmp/_vanilla_norm.txt > /tmp/_expr_diff.txt; then
    echo "RESULT: IDENTICAL  (native == vanilla)"
else
    echo "RESULT: DIFFERENCES FOUND"
    echo "----- diff (native < / vanilla >) -----"
    cat /tmp/_expr_diff.txt
fi

#!/bin/bash
# Normalize and diff OmniStream-native output vs vanilla-Flink output.
#
# Native (OmniStream, WRITE_TO_FILE=TRUE) writes  /tmp/flink_output.txt   as: +I,v1,v2,...
# Vanilla Flink `print` sink writes to TaskManager .out                  as: +I[v1, v2, ...]
#
# Usage:
#   bash compare_native_vanilla.sh <native_file> <vanilla_file>
# Example:
#   bash compare_native_vanilla.sh /tmp/flink_output.txt /tmp/vanilla_out.txt
#
# To capture vanilla output first:
#   grep -E '^\+I\[' /opt/flink/log/flink-*-taskexecutor-*.out > /tmp/vanilla_out.txt

NATIVE=${1:-/tmp/flink_output.txt}
VANILLA=${2:-/tmp/vanilla_out.txt}

normalize() {
    # Reads a file, emits canonical "v1|v2|v3..." per row, sorted.
    sed -E \
        -e 's/^\+I\[/+I,/' \
        -e 's/\]$//' \
        -e 's/^[+-]I,//' \
        -e 's/, /,/g' \
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

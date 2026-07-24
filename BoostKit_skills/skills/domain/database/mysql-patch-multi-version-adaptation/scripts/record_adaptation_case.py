#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("用法: record_adaptation_case.py <json_file> <jsonl_output>", file=sys.stderr)
        return 1

    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])

    if not src.is_file():
        print(f"错误: JSON 文件不存在: {src}", file=sys.stderr)
        return 1

    data = json.loads(src.read_text())
    required = [
        "date",
        "topic",
        "target_version",
        "selected_reference_branch",
        "compile_pass",
        "startup_pass",
        "functional_pass",
    ]
    missing = [k for k in required if k not in data]
    if missing:
        print(f"错误: 缺少必填字段: {', '.join(missing)}", file=sys.stderr)
        return 1

    dst.parent.mkdir(parents=True, exist_ok=True)
    with dst.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    print(f"已追加记录到 {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

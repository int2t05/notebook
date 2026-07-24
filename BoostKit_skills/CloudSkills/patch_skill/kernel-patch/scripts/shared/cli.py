"""
CLI helpers for kernel_patch scripts.
"""

import json
import sys
from typing import Any


def emit_json(payload: Any) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if isinstance(payload, dict) and payload.get("success") is False:
        return 1
    return 0


def load_json_arg(raw: str) -> Any:
    return json.loads(raw)


def load_json_file(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def exit_with_json(payload: Any) -> None:
    raise SystemExit(emit_json(payload))

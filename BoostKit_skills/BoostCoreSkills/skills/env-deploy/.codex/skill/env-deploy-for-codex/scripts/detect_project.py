#!/usr/bin/env python3
"""Detect project type and likely build/test commands for env-deploy-for-codex."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import env_deploy


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect env-deploy-for-codex project metadata.")
    parser.add_argument("project", nargs="?", default=".", help="Project root to inspect.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    detection = env_deploy.detect_project(project)
    data = detection.to_json()
    print(json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if data["primary_type"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

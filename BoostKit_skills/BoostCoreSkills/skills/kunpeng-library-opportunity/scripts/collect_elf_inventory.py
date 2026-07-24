#!/usr/bin/env python3
"""
Collect ELF, /proc, and library evidence for Kunpeng BoostKit opportunity review.

Run on the Linux target host whenever possible. The script uses only Python's
standard library and common Linux tools when available.
"""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path


MAX_TEXT = 120000

SIGNAL_PATTERNS = {
    "openssl_or_tls": [
        r"\blibssl\.so",
        r"\blibcrypto\.so",
        r"\bOPENSSL_",
        r"\bEVP_",
        r"\bSSL_",
        r"\bAES_",
        r"\bSHA(1|224|256|384|512)_",
        r"\bsha(1|224|256|384|512)[_-]",
        r"\bRSA_",
    ],
    "zlib": [r"\blibz\.so", r"\bdeflate", r"\binflate", r"\bgzip", r"\bz_stream"],
    "zstd": [r"\blibzstd\.so", r"\bZSTD_", r"\bzstd"],
    "lz4": [r"\bliblz4\.so", r"\bLZ4_", r"\blz4"],
    "snappy": [r"\blibsnappy\.so", r"\bsnappy::", r"\bsnappy"],
    "protobuf": [
        r"\blibprotobuf\.so",
        r"\bgoogle::protobuf",
        r"\bprotobuf::",
        r"\bParseFrom",
        r"\bSerializeTo",
    ],
    "json": [
        r"\brapidjson",
        r"\bsimdjson",
        r"\bnlohmann",
        r"\bjsoncpp",
        r"\bsonic",
        r"\bParseJson",
    ],
    "allocator": [
        r"\bmalloc\b",
        r"\bfree\b",
        r"\brealloc\b",
        r"\bcalloc\b",
        r"\blibjemalloc\.so",
        r"\blibtcmalloc",
        r"\blibkqmalloc",
    ],
    "glibc_hot_functions": [
        r"\bmemcpy\b",
        r"\bmemmove\b",
        r"\bmemcmp\b",
        r"\bmemset\b",
        r"\bstrlen\b",
        r"\bstrcmp\b",
        r"\bclock_gettime\b",
    ],
    "isa_l_or_crc": [r"\blibisal", r"\bisa-l", r"\bcrc32", r"\berasure", r"\bgf_"],
    "spdk": [r"\bspdk", r"\bbdev", r"\bnvme"],
    "avx_porting": [r"\bAVX2\b", r"\b_AVX", r"\b_mm256_", r"\bimmintrin\.h"],
    "kqmalloc_enabled": [r"\blibkqmalloc", r"\bKQMALLOC_"],
}

CANDIDATE_RULES = {
    "KAE": {
        "signals": ["openssl_or_tls", "zlib"],
        "reason": "TLS, crypto, or zlib-style compression evidence may map to KAE hardware acceleration.",
    },
    "KZL optimized compression": {
        "signals": ["zlib", "zstd", "lz4", "snappy"],
        "reason": "Compression libraries are present or suspected and can be checked against Kunpeng optimized patch repositories.",
    },
    "kpglibc": {
        "signals": ["glibc_hot_functions"],
        "reason": "String, memory, or time routine evidence may justify system-library benchmarking on Kunpeng.",
    },
    "protobuf": {
        "signals": ["protobuf"],
        "reason": "Protobuf serialization evidence may justify checking the Kunpeng optimized protobuf repository.",
    },
    "sonic-cpp": {
        "signals": ["json"],
        "reason": "JSON parse or serialize evidence may justify a sonic-cpp migration check if APIs are compatible.",
    },
    "KQMalloc": {
        "signals": ["allocator"],
        "reason": "Allocator evidence may justify KQMalloc validation on Kunpeng CPUs.",
    },
    "ISA-L": {
        "signals": ["isa_l_or_crc"],
        "reason": "CRC, erasure coding, or storage algorithm evidence may map to ISA-L opportunities.",
    },
    "KAE enabled SPDK": {
        "signals": ["spdk"],
        "reason": "SPDK evidence may justify checking BDEV compression or crypto acceleration paths.",
    },
    "AVX2KI": {
        "signals": ["avx_porting"],
        "reason": "AVX intrinsic evidence is a source-porting lead for Kunpeng migration.",
    },
}


def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def truncate(text, limit=MAX_TEXT):
    if text is None:
        return ""
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]..."


def run_command(args, timeout=10, max_text=MAX_TEXT):
    executable = shutil.which(args[0])
    record = {
        "args": args,
        "available": bool(executable),
        "returncode": None,
        "stdout": "",
        "stderr": "",
        "error": None,
    }
    if not executable:
        record["error"] = "command not found"
        return record
    try:
        proc = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        record["returncode"] = proc.returncode
        record["stdout"] = truncate(proc.stdout.decode("utf-8", "replace"), max_text)
        record["stderr"] = truncate(proc.stderr.decode("utf-8", "replace"), max_text)
    except Exception as exc:
        record["error"] = repr(exc)
    return record


def read_text(path, max_bytes=MAX_TEXT):
    try:
        with open(path, "rb") as handle:
            data = handle.read(max_bytes + 1)
        text = data[:max_bytes].decode("utf-8", "replace")
        if len(data) > max_bytes:
            text += "\n...[truncated]..."
        return {"ok": True, "text": text, "error": None}
    except Exception as exc:
        return {"ok": False, "text": "", "error": repr(exc)}


def read_nul_env(path):
    try:
        data = Path(path).read_bytes()
    except Exception as exc:
        return {"ok": False, "vars": {}, "error": repr(exc)}
    env = {}
    for item in data.split(b"\0"):
        if not item or b"=" not in item:
            continue
        key, value = item.split(b"=", 1)
        env[key.decode("utf-8", "replace")] = value.decode("utf-8", "replace")
    return {"ok": True, "vars": env, "error": None}


def parse_proc_maps(text):
    paths = []
    libraries = []
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        path = fields[-1]
        if not path.startswith("/"):
            continue
        path = path.replace(" (deleted)", "")
        paths.append(path)
        name = os.path.basename(path)
        if ".so" in name or name.startswith("ld-") or name.startswith("lib"):
            libraries.append(path)
    return {
        "mapped_files": sorted(set(paths)),
        "libraries": sorted(set(libraries)),
    }


def parse_ldd(text):
    libraries = []
    not_found = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "not found" in stripped:
            not_found.append(stripped)
            continue
        match = re.search(r"=>\s+(/\S+)", stripped)
        if match:
            libraries.append(match.group(1))
            continue
        if stripped.startswith("/"):
            libraries.append(stripped.split()[0])
    return {"libraries": sorted(set(libraries)), "not_found": not_found}


def parse_readelf_dynamic(text):
    needed = []
    rpath = []
    runpath = []
    for line in text.splitlines():
        if "(NEEDED)" in line:
            match = re.search(r"\[(.*?)\]", line)
            if match:
                needed.append(match.group(1))
        elif "(RPATH)" in line:
            match = re.search(r"\[(.*?)\]", line)
            if match:
                rpath.append(match.group(1))
        elif "(RUNPATH)" in line:
            match = re.search(r"\[(.*?)\]", line)
            if match:
                runpath.append(match.group(1))
    return {
        "needed": sorted(set(needed)),
        "rpath": sorted(set(rpath)),
        "runpath": sorted(set(runpath)),
    }


def os_release():
    info = read_text("/etc/os-release", max_bytes=20000)
    if not info["ok"]:
        return {"raw": "", "fields": {}, "error": info["error"]}
    fields = {}
    for line in info["text"].splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        fields[key] = value.strip().strip('"')
    return {"raw": info["text"], "fields": fields, "error": None}


def resolve_binary(pid, binary):
    if binary:
        return os.path.realpath(binary)
    if pid:
        try:
            return os.path.realpath(os.readlink(f"/proc/{pid}/exe"))
        except Exception:
            return None
    return None


def detect_signals(chunks):
    combined = "\n".join(chunk for chunk in chunks if chunk)
    hits = {}
    for signal, patterns in SIGNAL_PATTERNS.items():
        signal_hits = []
        for pattern in patterns:
            if re.search(pattern, combined, flags=re.IGNORECASE):
                signal_hits.append(pattern)
        if signal_hits:
            hits[signal] = signal_hits
    return hits


def build_candidates(signal_hits):
    candidates = []
    for name, rule in CANDIDATE_RULES.items():
        matched = [signal for signal in rule["signals"] if signal in signal_hits]
        if matched:
            candidates.append(
                {
                    "candidate": name,
                    "matched_signals": matched,
                    "reason": rule["reason"],
                    "confidence": "lead",
                }
            )
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Collect library evidence for a Linux ELF process or binary.")
    parser.add_argument("--pid", type=int, help="Running process ID to inspect")
    parser.add_argument("--binary", help="ELF binary path to inspect")
    parser.add_argument("--out", help="Write JSON output to this path")
    parser.add_argument("--skip-ldd", action="store_true", help="Do not run ldd")
    parser.add_argument("--include-strings", action="store_true", help="Run strings on the binary for static-link hints")
    parser.add_argument("--strings-limit", type=int, default=MAX_TEXT, help="Maximum strings output to keep")
    args = parser.parse_args()

    if not args.pid and not args.binary:
        parser.error("provide --pid, --binary, or both")

    binary = resolve_binary(args.pid, args.binary)
    commands = []
    chunks_for_detection = []

    result = {
        "schema_version": "1",
        "collected_at": now_iso(),
        "target": {
            "pid": args.pid,
            "binary": binary,
            "binary_argument": args.binary,
        },
        "environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "uname": " ".join(platform.uname()),
            "os_release": os_release(),
            "page_size": None,
            "transparent_hugepage": {},
        },
        "runtime": {
            "environment_readable": None,
            "ld_preload": None,
            "kqmalloc_env": {},
        },
        "dynamic_libraries": {
            "from_proc_maps": [],
            "from_ldd": [],
            "elf_needed": [],
            "not_found": [],
            "rpath": [],
            "runpath": [],
        },
        "static_or_embedded_hints": {},
        "signal_hits": {},
        "boostkit_candidate_signals": [],
        "commands": commands,
    }

    page_size = run_command(["getconf", "PAGESIZE"], timeout=5, max_text=2000)
    commands.append(page_size)
    if page_size["stdout"].strip():
        result["environment"]["page_size"] = page_size["stdout"].strip()

    for thp_name in ("enabled", "defrag"):
        thp_path = f"/sys/kernel/mm/transparent_hugepage/{thp_name}"
        thp = read_text(thp_path, max_bytes=2000)
        result["environment"]["transparent_hugepage"][thp_name] = thp

    if args.pid:
        env = read_nul_env(f"/proc/{args.pid}/environ")
        result["runtime"]["environment_readable"] = env["ok"]
        if env["ok"]:
            result["runtime"]["ld_preload"] = env["vars"].get("LD_PRELOAD")
            result["runtime"]["kqmalloc_env"] = {
                key: value for key, value in env["vars"].items() if key.startswith("KQMALLOC_")
            }
            chunks_for_detection.append("\n".join(f"{k}={v}" for k, v in env["vars"].items()))

        maps = read_text(f"/proc/{args.pid}/maps", max_bytes=MAX_TEXT * 2)
        result["proc_maps"] = {"readable": maps["ok"], "error": maps["error"]}
        if maps["ok"]:
            parsed_maps = parse_proc_maps(maps["text"])
            result["dynamic_libraries"]["from_proc_maps"] = parsed_maps["libraries"]
            result["mapped_files"] = parsed_maps["mapped_files"]
            chunks_for_detection.append("\n".join(parsed_maps["libraries"]))

    if binary:
        file_cmd = run_command(["file", binary], timeout=5, max_text=10000)
        commands.append(file_cmd)
        chunks_for_detection.append(file_cmd["stdout"])

        readelf_cmd = run_command(["readelf", "-d", binary], timeout=10, max_text=MAX_TEXT)
        commands.append(readelf_cmd)
        if readelf_cmd["stdout"]:
            parsed_dynamic = parse_readelf_dynamic(readelf_cmd["stdout"])
            result["dynamic_libraries"]["elf_needed"] = parsed_dynamic["needed"]
            result["dynamic_libraries"]["rpath"] = parsed_dynamic["rpath"]
            result["dynamic_libraries"]["runpath"] = parsed_dynamic["runpath"]
            chunks_for_detection.append(readelf_cmd["stdout"])

        objdump_cmd = run_command(["objdump", "-p", binary], timeout=10, max_text=MAX_TEXT)
        commands.append(objdump_cmd)
        chunks_for_detection.append(objdump_cmd["stdout"])

        if not args.skip_ldd:
            ldd_cmd = run_command(["ldd", binary], timeout=10, max_text=MAX_TEXT)
            commands.append(ldd_cmd)
            if ldd_cmd["stdout"]:
                parsed_ldd = parse_ldd(ldd_cmd["stdout"])
                result["dynamic_libraries"]["from_ldd"] = parsed_ldd["libraries"]
                result["dynamic_libraries"]["not_found"] = parsed_ldd["not_found"]
                chunks_for_detection.append(ldd_cmd["stdout"])

        nm_dynamic = run_command(["nm", "-D", binary], timeout=10, max_text=MAX_TEXT)
        commands.append(nm_dynamic)
        if nm_dynamic["stdout"]:
            result["static_or_embedded_hints"]["dynamic_symbols_scanned"] = True
            chunks_for_detection.append(nm_dynamic["stdout"])

        if args.include_strings:
            strings_cmd = run_command(
                ["strings", "-a", "-n", "6", binary],
                timeout=20,
                max_text=max(args.strings_limit, 1000),
            )
            commands.append(strings_cmd)
            if strings_cmd["stdout"]:
                result["static_or_embedded_hints"]["strings_scanned"] = True
                chunks_for_detection.append(strings_cmd["stdout"])
        else:
            result["static_or_embedded_hints"]["strings_scanned"] = False

    signal_hits = detect_signals(chunks_for_detection)
    result["signal_hits"] = signal_hits
    result["boostkit_candidate_signals"] = build_candidates(signal_hits)

    text = json.dumps(result, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)

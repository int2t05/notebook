#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlparse


SKILL_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = SKILL_DIR / "references" / "os-images.yaml"
MANAGED_MARKER = "managed-by=remote-vm-builder"
DEFAULT_ROOT_DIR = "auto"
SUPPORTED_IMAGE_SUFFIXES = (
    ".qcow2",
    ".img",
    ".raw",
    ".qcow2.xz",
    ".img.xz",
    ".raw.xz",
    ".qcow2.gz",
    ".img.gz",
    ".raw.gz",
)


class UserError(Exception):
    pass


def strip_yaml_comment(line: str) -> str:
    in_single = False
    in_double = False
    escaped = False
    for i, ch in enumerate(line):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_double:
            escaped = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if ch == "#" and not in_single and not in_double:
            if i == 0 or line[i - 1].isspace():
                return line[:i].rstrip()
    return line.rstrip()


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return ""
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value in {"null", "Null", "none", "None"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return ast.literal_eval(value)
    if value.startswith("[") and value.endswith("]"):
        return ast.literal_eval(value)
    if re.fullmatch(r"-?[0-9]+", value):
        return int(value)
    return value


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    root: Dict[str, Any] = {}
    stack: List[Tuple[int, Dict[str, Any]]] = [(-1, root)]

    for lineno, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = strip_yaml_comment(raw_line)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            raise UserError(f"unsupported YAML syntax at line {lineno}: {raw_line}")
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key:
            raise UserError(f"empty YAML key at line {lineno}")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise UserError(f"invalid YAML indentation at line {lineno}")
        parent = stack[-1][1]
        if value.strip() == "":
            child: Dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = parse_scalar(value)
    return root


def load_yaml(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
    except ModuleNotFoundError:
        data = parse_simple_yaml(text)
    if not isinstance(data, dict):
        raise UserError(f"{path} must contain a YAML mapping")
    return data


def load_catalog() -> Dict[str, Any]:
    catalog = load_yaml(CATALOG_PATH)
    if "images" not in catalog or not isinstance(catalog["images"], dict):
        raise UserError(f"{CATALOG_PATH} is missing an images mapping")
    return catalog


def normalize_arch(value: Optional[str]) -> str:
    if not value:
        return "auto"
    arch = value.strip().lower()
    aliases = {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86-64": "x86_64",
        "arm64": "aarch64",
        "armv8": "aarch64",
    }
    return aliases.get(arch, arch)


def q(value: Any) -> str:
    return shlex.quote(str(value))


def sanitize_name(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-")
    return safe or "remote-vm"


def image_basename(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return sanitize_name(name or fallback)


def uncompressed_name(name: str) -> str:
    for suffix in (".xz", ".gz"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def infer_compression(url: str) -> str:
    if url.endswith(".xz"):
        return "xz"
    if url.endswith(".gz"):
        return "gz"
    return "none"


def infer_image_format(url: str, explicit: Optional[str] = None) -> str:
    if explicit:
        return explicit
    name = uncompressed_name(image_basename(url, "image.qcow2"))
    if name.endswith(".raw"):
        return "raw"
    return "qcow2"


def catalog_rows(
    catalog: Dict[str, Any],
    family: Optional[str] = None,
    arch: Optional[str] = None,
    available_only: bool = False,
) -> List[Dict[str, Any]]:
    images = catalog["images"]
    arch = normalize_arch(arch) if arch else None
    rows = []
    for os_id, meta in images.items():
        if family and str(meta.get("family", "")).lower() != family.lower():
            continue
        arch_meta = meta.get("architectures", {})
        if arch and arch not in arch_meta:
            continue
        selected = {arch: arch_meta[arch]} if arch else arch_meta
        available_arches = [
            item_arch
            for item_arch, item in selected.items()
            if bool(item.get("available", True))
        ]
        if available_only and not available_arches:
            continue
        rows.append(
            {
                "os_id": os_id,
                "name": meta.get("name", os_id),
                "family": meta.get("family", ""),
                "version": meta.get("version", ""),
                "arches": list(selected.keys()),
                "available_arches": available_arches,
                "default_user": meta.get("default_user", ""),
                "status": "available" if available_arches else "unavailable",
                "note": meta.get("note", ""),
            }
        )
    return rows


def print_table(rows: List[Dict[str, Any]], columns: List[Tuple[str, str]]) -> None:
    if not rows:
        print("No matching entries.")
        return
    widths = []
    for key, header in columns:
        width = len(header)
        for row in rows:
            value = row.get(key, "")
            if isinstance(value, list):
                value = ",".join(str(v) for v in value)
            width = max(width, len(str(value)))
        widths.append(width)
    header_line = "  ".join(header.ljust(widths[i]) for i, (_, header) in enumerate(columns))
    print(header_line)
    print("  ".join("-" * width for width in widths))
    for row in rows:
        cells = []
        for i, (key, _) in enumerate(columns):
            value = row.get(key, "")
            if isinstance(value, list):
                value = ",".join(str(v) for v in value)
            cells.append(str(value).ljust(widths[i]))
        print("  ".join(cells))


def run_local(
    argv: List[str],
    *,
    input_text: Optional[str] = None,
    capture: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        argv,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise UserError(detail or f"command failed: {' '.join(argv)}")
    return result


def run_ssh_script(
    host: str,
    script: str,
    *,
    capture: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess:
    return run_local(["ssh", host, "bash", "-s"], input_text=script, capture=capture, check=check)


def parse_kv_output(text: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def capability_probe_script() -> str:
    return r"""
set +e
have() { command -v "$1" >/dev/null 2>&1 && echo yes || echo no; }
csv() { awk 'NF {print}' | paste -sd, -; }

echo "arch=$(uname -m 2>/dev/null)"
echo "sudo=$(sudo -n true >/dev/null 2>&1 && echo yes || echo no)"
echo "kvm=$([ -e /dev/kvm ] && echo yes || echo no)"
echo "virsh=$(have virsh)"
echo "virt_install=$(have virt-install)"
echo "qemu_img=$(have qemu-img)"
echo "curl=$(have curl)"
echo "xz=$(have xz)"
echo "gzip=$(have gzip)"
echo "cloud_localds=$(have cloud-localds)"
echo "genisoimage=$(have genisoimage)"
echo "mkisofs=$(have mkisofs)"

VIRSH=""
if command -v virsh >/dev/null 2>&1; then
  if virsh -c qemu:///system list --all >/dev/null 2>&1; then
    VIRSH="virsh -c qemu:///system"
  elif sudo -n virsh -c qemu:///system list --all >/dev/null 2>&1; then
    VIRSH="sudo -n virsh -c qemu:///system"
  fi
fi

if [ -n "$VIRSH" ]; then
  echo "libvirt=yes"
  echo "networks=$($VIRSH net-list --all --name 2>/dev/null | csv)"
  echo "active_networks=$($VIRSH net-list --name 2>/dev/null | csv)"
  echo "storage_pools=$($VIRSH pool-list --all --name 2>/dev/null | csv)"
  echo "active_storage_pools=$($VIRSH pool-list --name 2>/dev/null | csv)"
  echo "machine_types=$($VIRSH capabilities 2>/dev/null | sed -n 's/.*<machine[^>]*>\([^<]*\)<\/machine>.*/\1/p' | sort -u | csv)"
else
  echo "libvirt=no"
  echo "networks="
  echo "active_networks="
  echo "storage_pools="
  echo "active_storage_pools="
  echo "machine_types="
fi
"""


def remote_capabilities(host: str) -> Dict[str, Any]:
    result = run_ssh_script(host, capability_probe_script())
    raw = parse_kv_output(result.stdout or "")
    arch = normalize_arch(raw.get("arch"))
    raw["normalized_arch"] = arch
    raw["recommended_image_arch"] = arch if arch in {"x86_64", "aarch64"} else "unknown"
    for key in ("networks", "active_networks", "storage_pools", "active_storage_pools", "machine_types"):
        raw[key] = [item for item in raw.get(key, "").split(",") if item]
    raw["cpu_modes"] = ["host-passthrough", "host-model"] if raw.get("libvirt") == "yes" else []
    raw["virtualization"] = "kvm" if raw.get("kvm") == "yes" and raw.get("libvirt") == "yes" else "unavailable"
    return raw


def get_host_arch(host: str) -> str:
    result = run_ssh_script(host, "uname -m", capture=True)
    return normalize_arch((result.stdout or "").strip())


def yesno(value: Any) -> bool:
    return str(value).lower() == "yes"


def cmd_list_os(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    arch = args.arch
    host_arch = None
    if args.host:
        host_arch = get_host_arch(args.host)
        arch = host_arch
    rows = catalog_rows(catalog, args.family, arch, args.available_only)
    if args.json:
        print(json.dumps({"host_arch": host_arch, "images": rows}, indent=2, sort_keys=True))
        return 0
    if host_arch:
        print(f"Host architecture: {host_arch}")
    print_table(
        rows,
        [
            ("os_id", "OS ID"),
            ("name", "Name"),
            ("arches", "Arch"),
            ("default_user", "Default User"),
            ("status", "Status"),
        ],
    )
    return 0


def cmd_image_info(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    os_id = args.os
    if os_id == "custom":
        if not args.image_url:
            raise UserError("image-info --os custom requires --image-url")
        info = {
            "os_id": "custom",
            "image_url": args.image_url,
            "format": infer_image_format(args.image_url, args.image_format),
            "compressed": infer_compression(args.image_url),
            "available": True,
        }
    else:
        images = catalog["images"]
        if os_id not in images:
            raise UserError(f"unsupported OS ID: {os_id}. Run remote-vm list-os")
        meta = dict(images[os_id])
        arch = normalize_arch(args.arch) if args.arch else None
        arch_meta = meta.get("architectures", {})
        if arch:
            if arch not in arch_meta:
                raise UserError(f"{os_id} does not support architecture {arch}")
            meta["architectures"] = {arch: arch_meta[arch]}
        info = {"os_id": os_id, **meta}

    if args.json:
        print(json.dumps(info, indent=2, sort_keys=True))
        return 0

    print(f"OS ID: {info['os_id']}")
    if "name" in info:
        print(f"Name: {info['name']}")
        print(f"Family: {info.get('family', '')}")
        print(f"Default user: {info.get('default_user', '')}")
    if info["os_id"] == "custom":
        print(f"Image URL: {info['image_url']}")
        print(f"Format: {info['format']}")
        print(f"Compressed: {info['compressed']}")
    else:
        print("Architectures:")
        for item_arch, item in info.get("architectures", {}).items():
            status = "available" if item.get("available", True) else "unavailable"
            print(f"  {item_arch}: {status} {item.get('url', '')}")
        if info.get("note"):
            print(f"Note: {info['note']}")
    return 0


def print_capabilities(caps: Dict[str, Any]) -> None:
    print(f"Virtualization: {caps.get('virtualization', 'unknown')}")
    print(f"Architecture: {caps.get('normalized_arch', 'unknown')}")
    print(f"Machine types: {', '.join(caps.get('machine_types') or []) or 'unknown'}")
    print(f"CPU modes: {', '.join(caps.get('cpu_modes') or []) or 'unknown'}")
    print(f"Networks: {', '.join(caps.get('networks') or []) or 'none'}")
    print(f"Storage pools: {', '.join(caps.get('storage_pools') or []) or 'none'}")
    print(f"Recommended image arch: {caps.get('recommended_image_arch', 'unknown')}")


def cmd_host_info(args: argparse.Namespace) -> int:
    caps = remote_capabilities(args.host)
    if args.json:
        print(json.dumps(caps, indent=2, sort_keys=True))
    else:
        print_capabilities(caps)
    return 0


def cmd_list_vm_types(args: argparse.Namespace) -> int:
    caps = remote_capabilities(args.host)
    if args.json:
        payload = {
            key: caps.get(key)
            for key in (
                "virtualization",
                "normalized_arch",
                "machine_types",
                "cpu_modes",
                "networks",
                "storage_pools",
                "recommended_image_arch",
            )
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_capabilities(caps)
    return 0


def cmd_list_networks(args: argparse.Namespace) -> int:
    caps = remote_capabilities(args.host)
    rows = [{"network": n, "active": n in caps.get("active_networks", [])} for n in caps.get("networks", [])]
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print_table(rows, [("network", "Network"), ("active", "Active")])
    return 0


def cmd_list_storage_pools(args: argparse.Namespace) -> int:
    caps = remote_capabilities(args.host)
    rows = [
        {"storage_pool": p, "active": p in caps.get("active_storage_pools", [])}
        for p in caps.get("storage_pools", [])
    ]
    if args.json:
        print(json.dumps(rows, indent=2, sort_keys=True))
    else:
        print_table(rows, [("storage_pool", "Storage Pool"), ("active", "Active")])
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    try:
        caps = remote_capabilities(args.host)
        ssh_ok = True
        ssh_error = ""
    except UserError as exc:
        caps = {}
        ssh_ok = False
        ssh_error = str(exc)

    checks = [
        ("SSH connectivity", ssh_ok, ssh_error),
        ("sudo availability", yesno(caps.get("sudo")), "remote user needs sudo -n access"),
        ("libvirt service", yesno(caps.get("libvirt")), "virsh qemu:///system is not usable"),
        ("KVM availability", yesno(caps.get("kvm")), "/dev/kvm is missing"),
        ("qemu-img", yesno(caps.get("qemu_img")), "qemu-img is missing"),
        ("virt-install", yesno(caps.get("virt_install")), "virt-install is missing"),
        (
            "cloud-init seed tool",
            any(yesno(caps.get(k)) for k in ("cloud_localds", "genisoimage", "mkisofs")),
            "install cloud-localds, genisoimage, or mkisofs",
        ),
        ("default network", "default" in caps.get("networks", []), "libvirt network 'default' is missing"),
        (
            "storage pool",
            "default" in caps.get("storage_pools", []),
            "libvirt storage pool 'default' is missing",
        ),
        (
            "host architecture",
            caps.get("recommended_image_arch") in {"x86_64", "aarch64"},
            f"unsupported arch: {caps.get('arch', 'unknown')}",
        ),
    ]
    ok = all(item[1] for item in checks)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "host": args.host,
                    "recommended_image_arch": caps.get("recommended_image_arch"),
                    "checks": [
                        {"name": name, "ok": passed, "detail": "" if passed else detail}
                        for name, passed, detail in checks
                    ],
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        rows = [
            {"check": name, "status": "ok" if passed else "fail", "detail": "" if passed else detail}
            for name, passed, detail in checks
        ]
        print_table(rows, [("check", "Check"), ("status", "Status"), ("detail", "Detail")])
        if caps:
            print()
            print(f"Recommended image arch: {caps.get('recommended_image_arch', 'unknown')}")
    return 0 if ok else 1


def spec_get(spec: Dict[str, Any], path: Iterable[str], default: Any = None) -> Any:
    value: Any = spec
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return default
        value = value[key]
    return value


def read_public_key(value: Optional[str]) -> str:
    if value and re.match(r"^(ssh-|ecdsa-|sk-)", value.strip()):
        return value.strip()

    candidates = []
    if value:
        candidates.append(Path(value).expanduser())
    else:
        candidates.extend(
            [
                Path("~/.ssh/id_ed25519.pub").expanduser(),
                Path("~/.ssh/id_rsa.pub").expanduser(),
            ]
        )

    for path in candidates:
        if path.exists():
            key = path.read_text(encoding="utf-8").strip()
            if re.match(r"^(ssh-|ecdsa-|sk-)", key):
                return key
            raise UserError(f"public key file does not look like an SSH public key: {path}")
    raise UserError("no SSH public key found; pass --public-key ~/.ssh/id_ed25519.pub")


def merge_create_config(args: argparse.Namespace, catalog: Dict[str, Any]) -> Dict[str, Any]:
    defaults = catalog.get("defaults", {})
    spec: Dict[str, Any] = {}
    if args.spec:
        spec = load_yaml(Path(args.spec).expanduser())

    cfg: Dict[str, Any] = {
        "host": spec.get("host"),
        "name": spec.get("name"),
        "os": spec.get("os", "ubuntu-24.04"),
        "arch": spec.get("arch", defaults.get("arch", "auto")),
        "vcpus": spec_get(spec, ("resources", "vcpus"), defaults.get("vcpus", 4)),
        "memory_mb": spec_get(spec, ("resources", "memory_mb"), defaults.get("memory_mb", 8192)),
        "disk_gb": spec_get(spec, ("resources", "disk_gb"), defaults.get("disk_gb", 80)),
        "network": spec_get(spec, ("libvirt", "network"), defaults.get("network", "default")),
        "storage_pool": spec_get(
            spec, ("libvirt", "storage_pool"), defaults.get("storage_pool", "default")
        ),
        "cpu_mode": spec_get(spec, ("libvirt", "cpu_mode"), defaults.get("cpu_mode", "host-passthrough")),
        "vm_user": spec_get(spec, ("ssh", "user"), defaults.get("vm_user", "builder")),
        "public_key": spec_get(spec, ("ssh", "public_key"), None),
        "image_url": spec_get(spec, ("image", "url"), None),
        "image_checksum": spec_get(spec, ("image", "checksum"), None),
        "image_format": spec_get(spec, ("image", "format"), None),
        "root_dir": spec_get(spec, ("libvirt", "root_dir"), DEFAULT_ROOT_DIR),
    }

    cli_overrides = {
        "host": args.host,
        "name": args.name,
        "os": args.os,
        "arch": args.arch,
        "vcpus": args.vcpus,
        "memory_mb": args.memory_mb,
        "disk_gb": args.disk_gb,
        "network": args.network,
        "storage_pool": args.storage_pool,
        "cpu_mode": args.cpu_mode,
        "vm_user": args.vm_user,
        "public_key": args.public_key,
        "image_url": args.image_url,
        "image_checksum": args.image_checksum,
        "image_format": args.image_format,
        "root_dir": args.root_dir,
    }
    for key, value in cli_overrides.items():
        if value is not None:
            cfg[key] = value

    if not cfg["host"]:
        raise UserError("create requires --host or spec.host")
    if not cfg["name"]:
        cfg["name"] = f"{sanitize_name(str(cfg['os']))}-{int(time.time())}"
    cfg["name"] = sanitize_name(str(cfg["name"]))
    cfg["os"] = str(cfg["os"])
    cfg["arch"] = normalize_arch(str(cfg["arch"]))
    cfg["vcpus"] = int(cfg["vcpus"])
    cfg["memory_mb"] = int(cfg["memory_mb"])
    cfg["disk_gb"] = int(cfg["disk_gb"])
    return cfg


def select_image(catalog: Dict[str, Any], cfg: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    os_id = cfg["os"]
    image_url = cfg.get("image_url")

    if os_id != "custom" and image_url:
        raise UserError("--image-url is only supported with --os custom")

    if cfg["arch"] == "auto":
        cfg["arch"] = get_host_arch(cfg["host"])
    if cfg["arch"] not in {"x86_64", "aarch64"}:
        raise UserError(f"unsupported architecture: {cfg['arch']}")

    if os_id == "custom":
        if not image_url:
            raise UserError("--os custom requires --image-url")
        if not cfg.get("image_format") and not str(image_url).endswith(SUPPORTED_IMAGE_SUFFIXES):
            raise UserError("unknown image suffix; pass --image-format qcow2 or raw")
        image = {
            "url": image_url,
            "format": infer_image_format(image_url, cfg.get("image_format")),
            "compressed": infer_compression(image_url),
            "available": True,
        }
        meta = {
            "name": "Custom Linux cloud image",
            "default_user": cfg.get("vm_user", "builder"),
            "architectures": {cfg["arch"]: image},
        }
        return meta, image

    images = catalog["images"]
    if os_id not in images:
        raise UserError(f"unsupported OS ID: {os_id}. Run remote-vm list-os")
    meta = images[os_id]
    arch_meta = meta.get("architectures", {})
    if cfg["arch"] not in arch_meta:
        raise UserError(f"{os_id} does not support architecture {cfg['arch']}")
    image = arch_meta[cfg["arch"]]
    if not image.get("available", True):
        note = meta.get("note") or "the catalog marks this image unavailable"
        raise UserError(f"{os_id} {cfg['arch']} is unavailable: {note}")
    return meta, image


def checksum_script(checksum: Optional[str], path_var: str) -> str:
    if not checksum:
        return ""
    if not str(checksum).startswith("sha256:"):
        raise UserError("--image-checksum currently supports sha256:<digest>")
    digest = str(checksum).split(":", 1)[1]
    return textwrap.dedent(
        f"""
        echo {q(digest)}  "${path_var}" | sha256sum -c -
        """
    )


def create_remote_script(cfg: Dict[str, Any], image: Dict[str, Any], public_key: str) -> str:
    image_url = str(image["url"])
    compressed = str(image.get("compressed") or infer_compression(image_url))
    img_format = str(image.get("format") or infer_image_format(image_url))
    download_name = image_basename(image_url, f"{cfg['os']}-{cfg['arch']}.qcow2")
    base_name = uncompressed_name(download_name)
    cache_key_source = image_url if cfg["os"] == "custom" else f"{cfg['os']}-{cfg['arch']}"
    cache_key = sanitize_name(hashlib.sha256(cache_key_source.encode("utf-8")).hexdigest()[:16])
    hostname = sanitize_name(cfg["name"])[:63]
    root_dir = cfg.get("root_dir") or DEFAULT_ROOT_DIR

    script = f"""\
set -euo pipefail

VM_NAME={q(cfg['name'])}
OS_ID={q(cfg['os'])}
ARCH={q(cfg['arch'])}
IMAGE_URL={q(image_url)}
IMAGE_FORMAT={q(img_format)}
COMPRESSED={q(compressed)}
DOWNLOAD_NAME={q(download_name)}
BASE_NAME={q(base_name)}
CACHE_KEY={q(cache_key)}
ROOT_DIR={q(root_dir)}
STORAGE_POOL={q(cfg['storage_pool'])}
NETWORK={q(cfg['network'])}
VM_USER={q(cfg['vm_user'])}
PUBLIC_KEY={q(public_key)}
HOSTNAME={q(hostname)}
VCPUS={q(cfg['vcpus'])}
MEMORY_MB={q(cfg['memory_mb'])}
DISK_GB={q(cfg['disk_gb'])}
CPU_MODE={q(cfg['cpu_mode'])}

need() {{
  command -v "$1" >/dev/null 2>&1 || {{ echo "missing command: $1" >&2; exit 1; }}
}}

need curl
need qemu-img
need virt-install
need virsh
sudo -n true >/dev/null
[ -e /dev/kvm ] || {{ echo "/dev/kvm is missing; this host is not ready for KVM VMs" >&2; exit 1; }}

if sudo -n virsh -c qemu:///system dominfo "$VM_NAME" >/dev/null 2>&1; then
  echo "VM already exists: $VM_NAME" >&2
  exit 1
fi

sudo -n virsh -c qemu:///system pool-info "$STORAGE_POOL" >/dev/null
if [ "$ROOT_DIR" = "auto" ]; then
  POOL_PATH="$(sudo -n virsh -c qemu:///system pool-dumpxml "$STORAGE_POOL" | sed -n 's:.*<path>\\(.*\\)</path>.*:\\1:p' | head -n 1)"
  [ -n "$POOL_PATH" ] || {{ echo "storage pool $STORAGE_POOL has no filesystem path" >&2; exit 1; }}
  ROOT_DIR="${{POOL_PATH%/}}/remote-vm-builder"
fi

CACHE_DIR="${{ROOT_DIR%/}}/images/$CACHE_KEY"
WORK_DIR="${{ROOT_DIR%/}}/vms/$VM_NAME"
SEED_DIR="$WORK_DIR/seed"
RAW_DOWNLOAD="$CACHE_DIR/$DOWNLOAD_NAME"
BASE_IMAGE="$CACHE_DIR/$BASE_NAME"
DISK_IMAGE="$WORK_DIR/$VM_NAME.qcow2"
SEED_ISO="$WORK_DIR/seed.iso"

sudo -n mkdir -p "$CACHE_DIR" "$WORK_DIR" "$SEED_DIR"
sudo -n chown -R "$(id -u):$(id -g)" "$ROOT_DIR"

if [ ! -f "$BASE_IMAGE" ]; then
  if [ "$COMPRESSED" = "none" ]; then
    echo "Downloading image: $IMAGE_URL"
    curl -fL --retry 3 --retry-delay 2 -o "$BASE_IMAGE" "$IMAGE_URL"
"""
    if cfg.get("image_checksum"):
        script += checksum_script(str(cfg["image_checksum"]), "$BASE_IMAGE")
    script += """\
  else
    echo "Downloading compressed image: $IMAGE_URL"
    curl -fL --retry 3 --retry-delay 2 -o "$RAW_DOWNLOAD" "$IMAGE_URL"
"""
    if cfg.get("image_checksum"):
        script += checksum_script(str(cfg["image_checksum"]), "$RAW_DOWNLOAD")
    script += """\
    case "$COMPRESSED" in
      xz)
        need xz
        xz -dc "$RAW_DOWNLOAD" > "$BASE_IMAGE"
        ;;
      gz)
        need gzip
        gzip -dc "$RAW_DOWNLOAD" > "$BASE_IMAGE"
        ;;
      *)
        echo "unsupported compression: $COMPRESSED" >&2
        exit 1
        ;;
    esac
  fi
fi

BASE_FORMAT="$(qemu-img info "$BASE_IMAGE" | awk -F': ' '/file format/ {print $2; exit}')"
[ -n "$BASE_FORMAT" ] || BASE_FORMAT="$IMAGE_FORMAT"

if [ ! -f "$DISK_IMAGE" ]; then
  echo "Creating overlay disk: $DISK_IMAGE (${DISK_GB}G)"
  qemu-img create -f qcow2 -F "$BASE_FORMAT" -b "$BASE_IMAGE" "$DISK_IMAGE" "${DISK_GB}G" >/dev/null
fi

cat > "$SEED_DIR/meta-data" <<META
instance-id: $VM_NAME
local-hostname: $HOSTNAME
META

cat > "$SEED_DIR/user-data" <<USERDATA
#cloud-config
users:
  - default
  - name: $VM_USER
    gecos: Remote VM Builder
    groups: [adm, sudo, wheel]
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    lock_passwd: true
    ssh_authorized_keys:
      - $PUBLIC_KEY
ssh_pwauth: false
disable_root: false
package_update: false
USERDATA

rm -f "$SEED_ISO"
if command -v cloud-localds >/dev/null 2>&1; then
  cloud-localds "$SEED_ISO" "$SEED_DIR/user-data" "$SEED_DIR/meta-data"
elif command -v genisoimage >/dev/null 2>&1; then
  genisoimage -output "$SEED_ISO" -volid cidata -joliet -rock "$SEED_DIR/user-data" "$SEED_DIR/meta-data" >/dev/null 2>&1
elif command -v mkisofs >/dev/null 2>&1; then
  mkisofs -output "$SEED_ISO" -volid cidata -joliet -rock "$SEED_DIR/user-data" "$SEED_DIR/meta-data" >/dev/null 2>&1
else
  echo "missing cloud-init seed tool: install cloud-localds, genisoimage, or mkisofs" >&2
  exit 1
fi

NET_ARG="network=$NETWORK,model=virtio"
case "$NETWORK" in
  bridge:*) NET_ARG="bridge=${NETWORK#bridge:},model=virtio" ;;
  network:*) NET_ARG="network=${NETWORK#network:},model=virtio" ;;
esac

sudo -n virt-install \
  --connect qemu:///system \
  --name "$VM_NAME" \
  --import \
  --memory "$MEMORY_MB" \
  --vcpus "$VCPUS" \
  --cpu "$CPU_MODE" \
  --disk "path=$DISK_IMAGE,format=qcow2,bus=virtio" \
  --disk "path=$SEED_ISO,device=cdrom" \
  --network "$NET_ARG" \
  --os-variant detect=on,require=off \
  --graphics none \
  --noautoconsole \
  --boot hd

sudo -n virsh -c qemu:///system desc "$VM_NAME" --new-desc "${MANAGED_MARKER}; os=$OS_ID; user=$VM_USER; root=$WORK_DIR" >/dev/null
echo "Created VM: $VM_NAME"
echo "Root dir: $WORK_DIR"
"""
    return script


def get_vm_ip(host: str, name: str) -> str:
    script = f"""\
set +e
sudo -n virsh -c qemu:///system domifaddr {q(name)} --source lease 2>/dev/null | awk '/ipv4/ {{ split($4, a, "/"); print a[1]; exit }}'
"""
    result = run_ssh_script(host, script, capture=True, check=False)
    return (result.stdout or "").strip().splitlines()[0] if (result.stdout or "").strip() else ""


def wait_for_ip(host: str, name: str, timeout: int) -> str:
    deadline = time.time() + timeout
    while time.time() < deadline:
        ip = get_vm_ip(host, name)
        if ip:
            return ip
        time.sleep(5)
    return ""


def cmd_create(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    cfg = merge_create_config(args, catalog)
    _meta, image = select_image(catalog, cfg)
    public_key = read_public_key(cfg.get("public_key"))
    script = create_remote_script(cfg, image, public_key)

    if args.dry_run:
        print("# remote-vm create dry-run")
        print(json.dumps({k: v for k, v in cfg.items() if k != "public_key"}, indent=2, sort_keys=True))
        print()
        print(script)
        return 0

    run_ssh_script(cfg["host"], script, capture=False)
    if args.wait_timeout > 0:
        ip = wait_for_ip(cfg["host"], cfg["name"], args.wait_timeout)
        if ip:
            print(f"VM IP: {ip}")
            print(f"SSH: ssh -J {cfg['host']} {cfg['vm_user']}@{ip}")
        else:
            print("VM created, but no DHCP lease IP was found before timeout.")
    return 0


def vm_status_payload(host: str, name: str) -> Dict[str, str]:
    script = f"""\
set +e
STATE="$(sudo -n virsh -c qemu:///system domstate {q(name)} 2>/dev/null || echo absent)"
IP="$(sudo -n virsh -c qemu:///system domifaddr {q(name)} --source lease 2>/dev/null | awk '/ipv4/ {{ split($4, a, "/"); print a[1]; exit }}')"
DESC="$(sudo -n virsh -c qemu:///system desc {q(name)} 2>/dev/null || true)"
echo "state=$STATE"
echo "ip=$IP"
echo "description=$DESC"
"""
    result = run_ssh_script(host, script, capture=True, check=False)
    return parse_kv_output(result.stdout or "")


def cmd_status(args: argparse.Namespace) -> int:
    status = vm_status_payload(args.host, args.name)
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(f"Name: {args.name}")
        print(f"State: {status.get('state', 'unknown')}")
        print(f"IP: {status.get('ip') or 'unknown'}")
        print(f"Managed: {MANAGED_MARKER in status.get('description', '')}")
    return 0


def cmd_start(args: argparse.Namespace) -> int:
    run_ssh_script(
        args.host,
        f"sudo -n virsh -c qemu:///system start {q(args.name)}",
        capture=False,
    )
    return 0


def cmd_stop(args: argparse.Namespace) -> int:
    action = "destroy" if args.force else "shutdown"
    run_ssh_script(
        args.host,
        f"sudo -n virsh -c qemu:///system {action} {q(args.name)}",
        capture=False,
    )
    return 0


def cmd_destroy(args: argparse.Namespace) -> int:
    script = f"""\
set -euo pipefail
VM_NAME={q(args.name)}
FORCE={q("1" if args.force else "0")}
DESC="$(sudo -n virsh -c qemu:///system desc "$VM_NAME" 2>/dev/null || true)"
if [ "$FORCE" != "1" ] && ! printf '%s' "$DESC" | grep -q {q(MANAGED_MARKER)}; then
  echo "refusing to destroy VM not marked as remote-vm-builder managed; use --force to override" >&2
  exit 1
fi
ROOT="$(printf '%s' "$DESC" | sed -n 's/.*root=\\([^;]*\\).*/\\1/p')"
sudo -n virsh -c qemu:///system destroy "$VM_NAME" >/dev/null 2>&1 || true
sudo -n virsh -c qemu:///system undefine "$VM_NAME" --nvram >/dev/null 2>&1 || sudo -n virsh -c qemu:///system undefine "$VM_NAME" >/dev/null
if [ -n "$ROOT" ]; then
  sudo -n rm -rf "$ROOT"
fi
echo "Destroyed VM: $VM_NAME"
"""
    run_ssh_script(args.host, script, capture=False)
    return 0


def resolve_vm_ip_or_die(host: str, name: str) -> str:
    ip = get_vm_ip(host, name)
    if not ip:
        raise UserError(f"no VM IP found for {name}; run status or check libvirt DHCP leases")
    return ip


def cmd_ssh(args: argparse.Namespace) -> int:
    ip = resolve_vm_ip_or_die(args.host, args.name)
    argv = ["ssh", "-J", args.host, f"{args.vm_user}@{ip}"]
    os.execvp(argv[0], argv)
    return 0


def cmd_exec(args: argparse.Namespace) -> int:
    command = list(args.command or [])
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise UserError("exec requires a command after --")
    ip = resolve_vm_ip_or_die(args.host, args.name)
    result = subprocess.run(["ssh", "-J", args.host, f"{args.vm_user}@{ip}", "--", *command])
    return result.returncode


def add_host_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--host", required=True, help="SSH host alias or user@host for the remote VM server")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="remote-vm",
        description="Create and manage Linux cloud-image VMs on remote libvirt/KVM hosts.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("list-os", help="List built-in OS image IDs")
    p.add_argument("--family", help="Filter by OS family, e.g. openeuler")
    p.add_argument("--arch", help="Filter by architecture, e.g. x86_64 or aarch64")
    p.add_argument("--host", help="Filter by the remote host architecture")
    p.add_argument("--available-only", action="store_true", help="Hide catalog entries marked unavailable")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list_os)

    p = sub.add_parser("image-info", help="Show details for one OS image")
    p.add_argument("--os", required=True, help="OS ID or custom")
    p.add_argument("--arch", help="Architecture to inspect")
    p.add_argument("--image-url", help="Custom Linux cloud image URL")
    p.add_argument("--image-format", choices=["qcow2", "raw"], help="Format for custom images")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_image_info)

    p = sub.add_parser("doctor", help="Check whether a remote host can create VMs")
    add_host_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("host-info", help="Show remote host virtualization capabilities")
    add_host_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_host_info)

    p = sub.add_parser("list-vm-types", help="Show VM types/capabilities supported by the host")
    add_host_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list_vm_types)

    p = sub.add_parser("list-networks", help="List libvirt networks on the host")
    add_host_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list_networks)

    p = sub.add_parser("list-storage-pools", help="List libvirt storage pools on the host")
    add_host_arg(p)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_list_storage_pools)

    p = sub.add_parser("create", help="Create a VM")
    p.add_argument("--spec", help="YAML spec path")
    p.add_argument("--host", help="SSH host alias or user@host")
    p.add_argument("--os", help="Built-in OS ID or custom")
    p.add_argument("--image-url", help="Custom Linux cloud image URL, only with --os custom")
    p.add_argument("--image-format", choices=["qcow2", "raw"], help="Custom image format if suffix is ambiguous")
    p.add_argument("--image-checksum", help="Optional sha256:<digest> for downloaded image")
    p.add_argument("--name", help="VM name")
    p.add_argument("--arch", help="VM image architecture, or auto")
    p.add_argument("--vcpus", type=int, help="Number of vCPUs")
    p.add_argument("--memory-mb", type=int, help="RAM in MB")
    p.add_argument("--disk-gb", type=int, help="Overlay disk size in GB")
    p.add_argument("--network", help="Libvirt network name, network:<name>, or bridge:<name>")
    p.add_argument("--storage-pool", help="Libvirt storage pool used to place VM artifacts")
    p.add_argument("--cpu-mode", help="Libvirt CPU mode")
    p.add_argument("--vm-user", help="User to create inside the VM")
    p.add_argument("--public-key", help="SSH public key path or literal public key")
    p.add_argument("--root-dir", help="Remote artifact root directory; default uses the storage pool path")
    p.add_argument("--wait-timeout", type=int, default=180, help="Seconds to wait for a DHCP lease")
    p.add_argument("--dry-run", action="store_true", help="Print the remote script without executing it")
    p.set_defaults(func=cmd_create)

    for command_name in ("status", "start", "stop", "destroy", "ssh"):
        p = sub.add_parser(command_name, help=f"{command_name.capitalize()} a VM")
        add_host_arg(p)
        p.add_argument("--name", required=True, help="VM name")
        if command_name in {"status"}:
            p.add_argument("--json", action="store_true")
        if command_name in {"stop", "destroy"}:
            p.add_argument("--force", action="store_true")
        if command_name == "ssh":
            p.add_argument("--vm-user", default="builder", help="VM SSH user")
        p.set_defaults(func=globals()[f"cmd_{command_name.replace('-', '_')}"])

    p = sub.add_parser("exec", help="Run a command inside a VM over SSH ProxyJump")
    add_host_arg(p)
    p.add_argument("--name", required=True, help="VM name")
    p.add_argument("--vm-user", default="builder", help="VM SSH user")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_exec)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except UserError as exc:
        print(f"remote-vm: error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("remote-vm: interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())

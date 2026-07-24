import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = REPO_ROOT / "skills" / "remote-vm-builder"
SCRIPT = SKILL_ROOT / "scripts" / "remote_vm.py"
PUBLIC_KEY = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITestRemoteVmBuilderKey"


def run_cli(*args, check=True):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=SKILL_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {args}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def test_list_os_catalog_matches_current_scope():
    result = run_cli("list-os", "--json")
    payload = json.loads(result.stdout)
    ids = [item["os_id"] for item in payload["images"]]

    assert "ubuntu-24.04" in ids
    assert "ubuntu-22.04" in ids
    assert "debian-12" in ids
    assert "centos-stream-9" in ids
    assert "rocky-9" not in ids
    assert "almalinux-9" not in ids
    assert len([item for item in payload["images"] if item["family"] == "openeuler"]) == 8


def test_openeuler_filter_marks_2403_sp4_unavailable():
    result = run_cli("list-os", "--family", "openeuler", "--json")
    images = {item["os_id"]: item for item in json.loads(result.stdout)["images"]}

    assert set(images) == {
        "openeuler-22.03-lts-sp1",
        "openeuler-22.03-lts-sp2",
        "openeuler-22.03-lts-sp3",
        "openeuler-22.03-lts-sp4",
        "openeuler-24.03-lts-sp1",
        "openeuler-24.03-lts-sp2",
        "openeuler-24.03-lts-sp3",
        "openeuler-24.03-lts-sp4",
    }
    assert images["openeuler-24.03-lts-sp4"]["status"] == "unavailable"
    assert images["openeuler-24.03-lts-sp3"]["status"] == "available"


def test_image_info_custom_requires_url():
    result = run_cli("image-info", "--os", "custom", check=False)

    assert result.returncode == 2
    assert "requires --image-url" in result.stderr


def test_create_custom_image_dry_run_supports_configuration_flags():
    result = run_cli(
        "create",
        "--host",
        "build01",
        "--os",
        "custom",
        "--image-url",
        "https://example.com/company-ubuntu-24.04.qcow2",
        "--name",
        "company-test",
        "--arch",
        "x86_64",
        "--vcpus",
        "8",
        "--memory-mb",
        "16384",
        "--disk-gb",
        "120",
        "--network",
        "default",
        "--storage-pool",
        "fast-ssd",
        "--vm-user",
        "builder",
        "--public-key",
        PUBLIC_KEY,
        "--wait-timeout",
        "0",
        "--dry-run",
    )

    assert '"vcpus": 8' in result.stdout
    assert '"memory_mb": 16384' in result.stdout
    assert '"disk_gb": 120' in result.stdout
    assert "IMAGE_URL=https://example.com/company-ubuntu-24.04.qcow2" in result.stdout
    assert "STORAGE_POOL=fast-ssd" in result.stdout
    assert "sudo -n virt-install" in result.stdout


def test_create_from_yaml_spec_dry_run(tmp_path):
    spec = tmp_path / "vm.yaml"
    spec.write_text(
        f"""
host: build01
name: oe2403-test
os: openeuler-24.03-lts-sp3
arch: aarch64
resources:
  vcpus: 8
  memory_mb: 16384
  disk_gb: 120
libvirt:
  network: default
  storage_pool: fast-ssd
  cpu_mode: host-passthrough
ssh:
  user: builder
  public_key: "{PUBLIC_KEY}"
""",
        encoding="utf-8",
    )

    result = run_cli("create", "--spec", str(spec), "--wait-timeout", "0", "--dry-run")

    assert '"os": "openeuler-24.03-lts-sp3"' in result.stdout
    assert "ARCH=aarch64" in result.stdout
    assert "VCPUS=8" in result.stdout
    assert "MEMORY_MB=16384" in result.stdout
    assert "DISK_GB=120" in result.stdout
    assert "STORAGE_POOL=fast-ssd" in result.stdout


def test_create_unavailable_catalog_image_fails_before_ssh():
    result = run_cli(
        "create",
        "--host",
        "build01",
        "--os",
        "openeuler-24.03-lts-sp4",
        "--name",
        "oe-sp4",
        "--arch",
        "x86_64",
        "--public-key",
        PUBLIC_KEY,
        "--dry-run",
        check=False,
    )

    assert result.returncode == 2
    assert "unavailable" in result.stderr

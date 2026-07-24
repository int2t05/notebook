#!/usr/bin/env python3
"""Tests for _build_config_targets config mapping in PatchWorkflow."""

import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

# Add project root to path
_scripts_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_scripts_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from scripts.orchestrator.workflow import PatchWorkflow


class TestBuildConfigTargets(unittest.TestCase):

    def _make_workflow(self, config_files=None):
        """Create a PatchWorkflow with mocked StateManager."""
        config = {
            "target_repo": "/tmp/fake-repo",
            "target_branch": "main",
            "patches_dir": "/tmp/patches",
            "config_files": config_files or [],
            "patch_sets": [],
        }
        state_manager = MagicMock()
        state_manager.state = {
            "phase": "idle",
            "config": {},
            "progress": {},
            "iteration": {"current": 0, "max": 4},
            "runtime": {},
            "llm": {},
            "final": {},
        }
        return PatchWorkflow(config, state_manager)

    def test_config_targets_empty_config_files(self):
        """When config_files is empty, _build_config_targets returns None."""
        wf = self._make_workflow(config_files=[])
        result = wf._build_config_targets("/nonexistent/patch.patch")
        self.assertIsNone(result)

    def test_config_targets_no_config_source_in_patch(self):
        """When patch has no config source paths, return identity mapping."""
        config_files = ["/repo/config.aarch64", "/repo/config.aarch64-64k"]
        wf = self._make_workflow(config_files=config_files)

        patch_content = (
            "diff --git a/drivers/foo.c b/drivers/foo.c\n"
            "--- a/drivers/foo.c\n"
            "+++ b/drivers/foo.c\n"
            "@@ -1,1 +1,1 @@\n"
            "+int x = 1;\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(patch_content)
            f.flush()
            patch_file = f.name

        try:
            result = wf._build_config_targets(patch_file)
            self.assertIsNotNone(result)
            self.assertEqual(result, {
                "/repo/config.aarch64": ["/repo/config.aarch64"],
                "/repo/config.aarch64-64k": ["/repo/config.aarch64-64k"],
            })
        finally:
            os.unlink(patch_file)

    def test_config_targets_maps_source_defconfig(self):
        """When patch modifies a defconfig, map source path to config_files targets."""
        config_files = ["/repo/config.aarch64", "/repo/config.aarch64-64k"]
        wf = self._make_workflow(config_files=config_files)

        patch_content = (
            "diff --git a/arch/arm64/configs/openeuler_defconfig b/arch/arm64/configs/openeuler_defconfig\n"
            "--- a/arch/arm64/configs/openeuler_defconfig\n"
            "+++ b/arch/arm64/configs/openeuler_defconfig\n"
            "@@ -1,1 +1,2 @@\n"
            " CONFIG_FOO=y\n"
            "+CONFIG_VIRT_PLAT_DEV=y\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(patch_content)
            f.flush()
            patch_file = f.name

        try:
            result = wf._build_config_targets(patch_file)
            self.assertIsNotNone(result)
            self.assertIn("arch/arm64/configs/openeuler_defconfig", result)
            self.assertEqual(
                result["arch/arm64/configs/openeuler_defconfig"],
                ["/repo/config.aarch64", "/repo/config.aarch64-64k"],
            )
        finally:
            os.unlink(patch_file)

    def test_config_targets_identity_fallback_kignconfig(self):
        """When patch only touches Kconfig (not a mapping source), fall back to identity."""
        config_files = ["/repo/config.aarch64"]
        wf = self._make_workflow(config_files=config_files)

        patch_content = (
            "diff --git a/drivers/misc/Kconfig b/drivers/misc/Kconfig\n"
            "--- a/drivers/misc/Kconfig\n"
            "+++ b/drivers/misc/Kconfig\n"
            "@@ -100,6 +100,7 @@\n"
            " config VIRT_PLAT_DEV\n"
            "+\tdepends on ACPI_IORT\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
            f.write(patch_content)
            f.flush()
            patch_file = f.name

        try:
            result = wf._build_config_targets(patch_file)
            self.assertIsNotNone(result)
            self.assertEqual(result, {"/repo/config.aarch64": ["/repo/config.aarch64"]})
        finally:
            os.unlink(patch_file)


if __name__ == "__main__":
    unittest.main()

import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import analyze_rej_file as arf


class AnalyzeRejFileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.rejects = self.root / "rejects"
        self.rejects.mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _write_rej(self, name: str, content: str) -> Path:
        path = self.rejects / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_compact_output_omits_full_hunks_and_includes_summaries(self) -> None:
        rej = self._write_rej(
            "irq-mbigen.c.rej",
            """diff --git a/drivers/irqchip/irq-mbigen.c b/drivers/irqchip/irq-mbigen.c
--- a/drivers/irqchip/irq-mbigen.c
+++ b/drivers/irqchip/irq-mbigen.c
@@ -58,2 +58,8 @@
 #define REG_MBIGEN_SPI_TYPE_OFFSET\t0x400
 #endif
+#ifdef CONFIG_VIRT_VTIMER_IRQ_BYPASS
+#include <linux/list.h>
+
+#include <linux/cpumask.h>
+#include <linux/cpuhotplug.h>
+#include <asm/smp_plat.h>
 /**
""",
        )
        payload = json.loads(arf.analyze_rej_file(str(rej), str(self.repo)))

        self.assertTrue(payload["success"])
        self.assertNotIn("hunks", payload)
        self.assertEqual(payload["statistics"]["hunk_count"], 1)
        self.assertEqual(payload["conflict_class"], "manual-edit-risk")
        self.assertIn("hunk_summaries", payload)
        summary = payload["hunk_summaries"][0]
        self.assertEqual(summary["added_line_count"], 6)
        self.assertEqual(summary["context_line_count"], 3)
        self.assertEqual(len(summary["added_preview"]), 3)
        self.assertEqual(summary["added_preview"][0], "#ifdef CONFIG_VIRT_VTIMER_IRQ_BYPASS")
        self.assertEqual(payload["suggested_next_step"], "只按当前 hunk 在目标文件局部对齐，不要扩展到别的文件。")

    def test_full_output_keeps_hunks(self) -> None:
        rej = self._write_rej(
            "cfg.rej",
            """diff --git a/arch/arm64/configs/openeuler_defconfig b/arch/arm64/configs/openeuler_defconfig
--- a/arch/arm64/configs/openeuler_defconfig
+++ b/arch/arm64/configs/openeuler_defconfig
@@ -10,1 +10,2 @@
 CONFIG_HISILICON_IRQ_MBIGEN=y
+CONFIG_VIRT_VTIMER_IRQ_BYPASS=y
""",
        )
        payload = json.loads(arf.analyze_rej_file(str(rej), str(self.repo), output_level="full"))

        self.assertTrue(payload["success"])
        self.assertIn("hunks", payload)
        self.assertNotIn("hunk_summaries", payload)
        self.assertEqual(payload["conflict_class"], "config-sync")
        self.assertEqual(payload["suggested_next_step"], "只同步到映射后的 config_files，不要修改原 defconfig 路径。")

    def test_compact_preview_truncates_long_lines(self) -> None:
        long_line = "A" * 180
        rej = self._write_rej(
            "long.rej",
            f"""diff --git a/foo.c b/foo.c
--- a/foo.c
+++ b/foo.c
@@ -1,1 +1,2 @@
 context
+{long_line}
""",
        )
        payload = json.loads(arf.analyze_rej_file(str(rej), str(self.repo), output_level="compact"))

        preview = payload["hunk_summaries"][0]["added_preview"][0]
        self.assertEqual(len(preview), arf.PREVIEW_CHAR_LIMIT)


if __name__ == "__main__":
    unittest.main()

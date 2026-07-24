import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_tests_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_tests_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

from scripts import validate_patches


def git(repo: str, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", repo, *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class ValidatePatchesBinaryDiffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.temp_dir.name, "repo")
        os.makedirs(self.repo, exist_ok=True)
        git(self.repo, "init")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def commit_file(self, relative_path: str, content: bytes, message: str) -> str:
        file_path = Path(self.repo) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(content)
        git(self.repo, "add", relative_path)
        git(self.repo, "commit", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def test_get_commit_diff_bytes_and_patch_id_support_binary_commits(self) -> None:
        self.commit_file("notes.txt", b"hello\n", "text commit")
        binary_commit = self.commit_file("blob.bin", bytes(range(256)), "binary commit")

        diff_bytes = validate_patches.get_commit_diff_bytes(self.repo, binary_commit)

        self.assertIsInstance(diff_bytes, bytes)
        self.assertTrue(
            b"GIT binary patch" in diff_bytes or b"Binary files " in diff_bytes
        )
        self.assertTrue(validate_patches.compute_patch_id(self.repo, diff_bytes))

    def test_compare_patch_to_commit_skips_binary_files(self) -> None:
        binary_patch = "\n".join(
            [
                "diff --git a/blob.bin b/blob.bin",
                "new file mode 100644",
                "index 0000000..1111111",
                "GIT binary patch",
                "literal 3",
                "KcmZQz",
                "",
            ]
        )

        differences = validate_patches.compare_patch_to_commit(binary_patch, binary_patch)

        self.assertEqual(1, len(differences))
        self.assertEqual("skipped", differences[0]["status"])
        self.assertIn("skipped", differences[0]["message"])

    def test_compare_patch_to_commit_keeps_text_diffs_comparable(self) -> None:
        local_patch = "\n".join(
            [
                "diff --git a/app.txt b/app.txt",
                "--- a/app.txt",
                "+++ b/app.txt",
                "@@ -1 +1 @@",
                "-old",
                "+new",
                "",
            ]
        )

        differences = validate_patches.compare_patch_to_commit(local_patch, local_patch)

        self.assertEqual(1, len(differences))
        self.assertEqual("identical", differences[0]["status"])


class ValidatePatchesSearchScopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.temp_dir.name, "repo")
        os.makedirs(self.repo, exist_ok=True)
        git(self.repo, "init")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")

        Path(self.repo, "base.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "base.txt")
        git(self.repo, "commit", "-m", "base commit")
        self.main_branch = git(self.repo, "rev-parse", "--abbrev-ref", "HEAD")

        git(self.repo, "checkout", "-b", "feature")
        git(self.repo, "branch", "--set-upstream-to", self.main_branch, "feature")

        Path(self.repo, "feature.txt").write_text("feature-1\n", encoding="utf-8")
        git(self.repo, "add", "feature.txt")
        git(self.repo, "commit", "-m", "feature commit 1")

        Path(self.repo, "feature.txt").write_text("feature-2\n", encoding="utf-8")
        git(self.repo, "add", "feature.txt")
        git(self.repo, "commit", "-m", "feature commit 2")

        self.head = git(self.repo, "rev-parse", "HEAD")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_build_target_commit_index_defaults_to_upstream_range(self) -> None:
        index = validate_patches.build_target_commit_index(self.repo, "feature")

        self.assertEqual("scoped", index.search_scope)
        self.assertEqual(self.main_branch, index.upstream_branch)
        self.assertEqual(2, len(index.commits))

    def test_build_target_commit_index_supports_global_search(self) -> None:
        index = validate_patches.build_target_commit_index(self.repo, "feature", global_search=True)

        self.assertEqual("global", index.search_scope)
        self.assertEqual("", index.upstream_branch)
        self.assertEqual(3, len(index.commits))

    def test_build_target_commit_index_fails_without_upstream(self) -> None:
        git(self.repo, "checkout", self.main_branch)
        git(self.repo, "checkout", "-b", "no-upstream")

        with self.assertRaisesRegex(ValueError, "cannot auto-detect upstream"):
            validate_patches.build_target_commit_index(self.repo, "no-upstream")

    def test_explicit_commit_overrides_scope_controls(self) -> None:
        index = validate_patches.build_target_commit_index(
            self.repo,
            "feature",
            explicit_commit=self.head,
            upstream_branch=self.main_branch,
            global_search=True,
        )

        self.assertEqual("explicit", index.search_scope)
        self.assertEqual(1, len(index.commits))
        self.assertEqual(self.head, index.commits[0].commit)


class ValidatePatchesMergedDiffMatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.temp_dir.name, "repo")
        self.patch_dir = os.path.join(self.temp_dir.name, "patches")
        os.makedirs(self.repo, exist_ok=True)
        os.makedirs(self.patch_dir, exist_ok=True)
        git(self.repo, "init")
        git(self.repo, "config", "user.name", "Test User")
        git(self.repo, "config", "user.email", "test@example.com")

        Path(self.repo, "base.txt").write_text("base\n", encoding="utf-8")
        git(self.repo, "add", "base.txt")
        git(self.repo, "commit", "-m", "base commit")
        self.branch = git(self.repo, "rev-parse", "--abbrev-ref", "HEAD")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def commit_text_file(self, relative_path: str, content: str, message: str) -> str:
        file_path = Path(self.repo) / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        git(self.repo, "add", relative_path)
        git(self.repo, "commit", "-m", message)
        return git(self.repo, "rev-parse", "HEAD")

    def write_patch_from_commit(self, patch_name: str, commit: str, subject: str, from_hash: str) -> str:
        author = git(self.repo, "show", "-s", "--format=%an <%ae>", commit)
        date = git(self.repo, "show", "-s", "--format=%aD", commit)
        diff_body = git(self.repo, "show", "--format=", "--unified=3", commit)
        patch_text = "\n".join(
            [
                f"From {from_hash} Mon Sep 17 00:00:00 2001",
                f"From: {author}",
                f"Date: {date}",
                f"Subject: [PATCH] {subject}",
                "",
                "---",
                diff_body.rstrip("\n"),
                "",
            ]
        )
        patch_path = Path(self.patch_dir) / patch_name
        patch_path.write_text(patch_text, encoding="utf-8")
        return str(patch_path)

    def test_merged_diff_matches_by_strict_subject_without_hash_fallback(self) -> None:
        commit = self.commit_text_file(
            "drivers/ipiv.txt",
            "strict\n",
            "KVM: arm64: Implement PV SGI related calls",
        )
        self.write_patch_from_commit(
            "deadbee_patch.patch",
            commit,
            "KVM: arm64: Implement PV SGI related calls",
            "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
        )

        result = validate_patches.validate_patches(
            self.patch_dir,
            self.repo,
            self.branch,
            validate_patches.ValidationMode.MERGED_DIFF.value,
            tolerance=3,
            threshold=0.9,
            global_search=True,
        )

        self.assertEqual("subject-strict->subject-fuzzy->diff", result.match_strategy)
        self.assertEqual(1, len(result.patches))
        self.assertEqual("MATCHED", result.patches[0]["target_match_status"])
        self.assertEqual("subject-strict", result.patches[0]["target_match_method"])

    def test_merged_diff_matches_by_fuzzy_subject_before_diff(self) -> None:
        commit = self.commit_text_file(
            "drivers/pvsgi.txt",
            "fuzzy\n",
            "KVM: arm64: Implement PV SGI related calls",
        )
        self.write_patch_from_commit(
            "fuzzy_subject.patch",
            commit,
            "KVM: arm64: Implement PV SGI related call set",
            "1234567890abcdef1234567890abcdef12345678",
        )

        result = validate_patches.validate_patches(
            self.patch_dir,
            self.repo,
            self.branch,
            validate_patches.ValidationMode.MERGED_DIFF.value,
            tolerance=3,
            threshold=0.9,
            global_search=True,
        )

        self.assertEqual(1, len(result.patches))
        self.assertEqual("MATCHED", result.patches[0]["target_match_status"])
        self.assertEqual("subject-fuzzy", result.patches[0]["target_match_method"])

    def test_merged_diff_uses_diff_when_subject_does_not_match(self) -> None:
        commit = self.commit_text_file(
            "drivers/diff.txt",
            "diff\n",
            "KVM: arm64: Introduce ipiv enable ioctl",
        )
        self.write_patch_from_commit(
            "diff_only.patch",
            commit,
            "totally unrelated patch title",
            "feedfacefeedfacefeedfacefeedfacefeedface",
        )

        result = validate_patches.validate_patches(
            self.patch_dir,
            self.repo,
            self.branch,
            validate_patches.ValidationMode.MERGED_DIFF.value,
            tolerance=3,
            threshold=0.9,
            global_search=True,
        )

        self.assertEqual(1, len(result.patches))
        self.assertEqual("MATCHED", result.patches[0]["target_match_status"])
        self.assertEqual("diff", result.patches[0]["target_match_method"])


if __name__ == "__main__":
    unittest.main()

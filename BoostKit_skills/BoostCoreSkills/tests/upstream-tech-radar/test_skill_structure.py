from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "upstream-tech-radar"
README_PATH = REPO_ROOT / "README.md"


def test_skill_directory_layout():
    expected_paths = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "README.md",
        SKILL_DIR / "references" / "analysis-dimensions.md",
        SKILL_DIR / "references" / "monthly-report-template.md",
        SKILL_DIR / "references" / "repo-comparison-playbook.md",
        REPO_ROOT / "docs" / "upstream-tech-radar-design.md",
    ]

    for path in expected_paths:
        assert path.exists(), f"missing required path: {path}"


def test_skill_frontmatter():
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(
        r"^---\nname:\s*(?P<name>[^\n]+)\ndescription:\s*(?P<description>[^\n]+)\n---\n",
        content,
    )
    assert match, "SKILL.md must start with YAML frontmatter containing name and description"
    assert match.group("name").strip() == "upstream-tech-radar"
    assert match.group("description").strip().startswith("Use when")


def test_references_linked_from_docs_exist():
    files_to_check = [
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "README.md",
    ]
    for path in files_to_check:
        content = path.read_text(encoding="utf-8")
        referenced = re.findall(r"\((?:\./)?(references/[^)]+)\)", content)
        for rel_path in referenced:
            target = SKILL_DIR / rel_path
            assert target.exists(), f"{path} references missing file: {rel_path}"


def test_root_readme_indexes_skill():
    content = README_PATH.read_text(encoding="utf-8")
    assert "upstream-tech-radar" in content
    assert "skills/upstream-tech-radar" in content


def test_skill_mentions_arm_viewpoint():
    content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Arm " in content
    assert "GitHub" in content


def test_readme_mentions_realtime_constraints():
    content = (SKILL_DIR / "README.md").read_text(encoding="utf-8")
    assert "GitHub API" in content or "GitHub" in content
    assert "最近 30 天" in content


def test_skill_mentions_instruction_level_value():
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    readme = (SKILL_DIR / "README.md").read_text(encoding="utf-8")
    assert "SVE" in skill or "SIMD" in skill
    assert "HISTSEG" in skill or "SVE2" in skill
    assert "issue" in skill and "10" in skill
    assert "HISTSEG" in readme or "SVE2" in readme
    assert "issue" in readme and "10" in readme


def test_skill_requires_deep_analysis_for_high_value_items():
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    readme = (SKILL_DIR / "README.md").read_text(encoding="utf-8")
    analysis = (SKILL_DIR / "references" / "analysis-dimensions.md").read_text(encoding="utf-8")
    template = (SKILL_DIR / "references" / "monthly-report-template.md").read_text(encoding="utf-8")

    for content in [skill, readme]:
        assert "discussion" in content
        assert "review" in content
        assert "diff" in content or "patch" in content
        assert "高价值条目" in content
        assert "作用" in content
        assert "场景" in content

    assert "discussion" in analysis
    assert "diff" in analysis or "patch" in analysis
    assert "更适合什么 workload" in analysis

    assert "讨论里暴露的争议点" in template
    assert "代码改动触达的核心路径" in template
    assert "更适合的应用场景 / workload" in template

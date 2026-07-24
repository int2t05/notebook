from pathlib import Path
import yaml
from scripts.renderer import render_archive


def test_render_archive_produces_three_md_files(tmp_archive, sample_papers):
    config = yaml.safe_load(Path(__file__).parent.parent.parent.parent
                            .joinpath("skills/paper-digest/config.yaml").read_text())
    # Add tags + summaries so renderer can fill template
    for p in sample_papers:
        p["relevance"] = "green"
        p["relevance_reason"] = "match"
        p["summary"] = {
            "background": "bg", "core": "co", "effect": "提升 50%",
            "effect_quantified": True, "insight": "in",
        }
        p["tags"] = {"industry": "academic", "opensource": "no", "deployability": "medium"}

    conferences = [{
        "name": "ISMM", "year": 2025, "dates": "2025-06-17", "venue": "Seoul",
        "total_papers": 1, "program_url": "https://example.com",
        "composite_score": 9.2,
    }]
    render_archive(
        archive_dir=tmp_archive,
        manifest={
            "input": {"direction_raw": "memory"},
            "parsed": {
                "keywords": ["memory"],
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
            },
            "created_at": "2026-05-22T10:00:00Z",
        },
        conferences=conferences,
        conf_papers=[sample_papers[0]],
        external_papers=[sample_papers[1]],
        tag_emoji=config["tags"],
    )
    assert (tmp_archive / "overview.md").exists()
    assert (tmp_archive / "conferences" / "ISMM-2025.md").exists()
    assert (tmp_archive / "external-sources.md").exists()

    overview = (tmp_archive / "overview.md").read_text()
    assert "memory" in overview
    assert "ISMM" in overview

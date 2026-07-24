"""Tests for Phase 0.5 (LLM-driven keyword expansion)."""
import json
from unittest.mock import MagicMock

import pytest

from scripts.focus_areas import (
    generate_via_llm, flatten_keywords, merge_into_synonym_map, to_markdown,
)


_VALID_LLM_RESPONSE = json.dumps({
    "primary": [
        {"name": "Memory allocators", "keywords": [
            "memory allocator", "malloc", "tcmalloc", "jemalloc",
            "mimalloc", "heap allocation", "slab allocator",
        ]},
    ],
    "secondary": [
        {"name": "Memory tiering", "keywords": [
            "tiered memory", "memory tiering", "page placement",
            "page migration", "hot/cold",
        ]},
    ],
    "tertiary": [
        {"name": "Compiler memory passes", "keywords": [
            "compiler optimization", "LLVM pass", "polyhedral",
        ]},
    ],
    "exclude": ["blockchain", "homomorphic encryption"],
    "arxiv_categories": ["cs.OS", "cs.PL", "cs.AR"],
})


def test_generate_via_llm_returns_structured_dict():
    llm = MagicMock()
    llm.call.return_value = (_VALID_LLM_RESPONSE, 500)
    out = generate_via_llm("memory allocator", ["memory", "malloc"], [], llm)
    assert out["primary"][0]["name"] == "Memory allocators"
    assert "cs.OS" in out["arxiv_categories"]
    assert "blockchain" in out["exclude"]
    # Default scoring_dimensions filled in
    assert "影响力" in out["scoring_dimensions"]


def test_generate_via_llm_handles_relaxed_json():
    """Tolerates markdown fences and smart quotes via relaxed_json_loads."""
    llm = MagicMock()
    llm.call.return_value = (
        '```json\n' + _VALID_LLM_RESPONSE + '\n```', 500)
    out = generate_via_llm("x", ["y"], [], llm)
    assert out["primary"]


def test_generate_via_llm_raises_on_garbage():
    llm = MagicMock()
    llm.call.return_value = ("totally not json {{{", 100)
    with pytest.raises(ValueError, match="unparseable JSON"):
        generate_via_llm("x", ["y"], [], llm)


def test_flatten_keywords_dedupes_across_levels():
    focus = {
        "primary": [{"name": "A", "keywords": ["a", "b"]}],
        "secondary": [{"name": "B", "keywords": ["b", "c"]}],
        "tertiary": [{"name": "C", "keywords": ["c", "d"]}],
    }
    out = flatten_keywords(focus)
    assert out == ["a", "b", "c", "d"]


def test_merge_into_synonym_map_overrides_base():
    """LLM-driven Phase 0.5 takes precedence over the profile's static map."""
    focus = {
        "primary": [{"name": "x", "keywords": ["memory allocator", "malloc"]}],
        "secondary": [],
        "tertiary": [],
    }
    base = {"memory allocator": ["old-variant-only"]}
    merged = merge_into_synonym_map(focus, base_synonym_map=base)
    assert merged["memory allocator"] == ["memory allocator", "malloc"]


def test_to_markdown_includes_all_sections():
    focus = json.loads(_VALID_LLM_RESPONSE)
    md = to_markdown(focus, "memory allocator", ["memory", "malloc"])
    assert "🎯 一级方向" in md
    assert "🔧 二级方向" in md
    assert "📚 三级方向" in md
    assert "❌ 不重点关注" in md
    assert "🗂️ arXiv 类目" in md
    assert "blockchain" in md

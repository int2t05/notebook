import pytest
from unittest.mock import MagicMock, patch
from scripts.extractor import (
    is_effect_quantified, extract_one, EXTRACT_ERROR_PLACEHOLDER,
)


@pytest.mark.parametrize("text,expected", [
    ("相比 HawkEye 性能提升最高 69%", True),
    ("速度提升 2.5x，内存减少 30%", True),
    ("延迟降至 1.2 ms", True),
    ("[未量化] 论文未给基线对比", True),
    ("性能显著提升", False),
    ("效果不错", False),
    ("", False),
])
def test_is_effect_quantified(text, expected):
    assert is_effect_quantified(text) == expected


def test_extract_one_validates_quantification_and_retries():
    llm = MagicMock()
    # First call: bad (no number, no [未量化])
    # Second call: good (has 50%)
    llm.call.side_effect = [
        ('{"summary":{"background":"x","core":"y","effect":"性能提升","insight":"z"},'
         '"tags":{"industry":"academic","opensource":"no","deployability":"medium"},'
         '"tag_notes":{}}', 500),
        ('{"summary":{"background":"x","core":"y","effect":"提升 50%","insight":"z"},'
         '"tags":{"industry":"academic","opensource":"no","deployability":"medium"},'
         '"tag_notes":{}}', 500),
    ]
    paper = {"id": "C-X-2025-001", "title": "T", "authors": ["A"],
             "affiliation": "U", "abstract": "x"}
    result = extract_one(paper, keywords=["m"], llm=llm)
    assert result["summary"]["effect"] == "提升 50%"
    assert result["summary"]["effect_quantified"] is True
    assert llm.call.call_count == 2


def test_extract_one_forces_placeholder_after_retry():
    llm = MagicMock()
    # Both calls produce non-quantified effect
    bad_resp = ('{"summary":{"background":"x","core":"y","effect":"很厉害","insight":"z"},'
                '"tags":{"industry":"academic","opensource":"no","deployability":"medium"},'
                '"tag_notes":{}}', 500)
    llm.call.side_effect = [bad_resp, bad_resp]
    paper = {"id": "C-X-2025-001", "title": "T", "authors": ["A"],
             "affiliation": "U", "abstract": "x"}
    result = extract_one(paper, keywords=["m"], llm=llm)
    assert result["summary"]["effect"].startswith("[未量化]")
    assert result["summary"]["effect_quantified"] is False

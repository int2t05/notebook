import json
import pytest

from scripts.utils import relaxed_json_loads


def test_strict_json_passes_through():
    assert relaxed_json_loads('{"a":1}') == {"a": 1}


def test_strips_markdown_fence():
    assert relaxed_json_loads('```json\n{"a":1}\n```') == {"a": 1}


def test_strips_prose_around_object():
    payload = 'Sure, here is the JSON:\n{"keywords": ["x"]}\nLet me know if you need more.'
    assert relaxed_json_loads(payload) == {"keywords": ["x"]}


def test_smart_quotes_recovered():
    payload = '{“a”: 1, “b”: “hi”}'
    assert relaxed_json_loads(payload) == {"a": 1, "b": "hi"}


def test_bare_newlines_in_string_recovered():
    payload = '{"summary":"line1\nline2"}'
    assert relaxed_json_loads(payload) == {"summary": "line1\nline2"}


def test_unrecoverable_raises():
    with pytest.raises(json.JSONDecodeError):
        relaxed_json_loads("totally not json {{{ ")

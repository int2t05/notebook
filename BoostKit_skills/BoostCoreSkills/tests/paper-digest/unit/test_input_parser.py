from datetime import date
from scripts.input_parser import parse_time_window, generate_slug


def test_parse_time_window_last_6_months(monkeypatch):
    monkeypatch.setattr("scripts.input_parser._today", lambda: date(2026, 5, 22))
    start, end = parse_time_window("last 6 months")
    assert end == date(2026, 5, 22)
    assert start == date(2025, 11, 22)


def test_parse_time_window_explicit_range():
    start, end = parse_time_window("2025-11-01..2026-05-01")
    assert start == date(2025, 11, 1)
    assert end == date(2026, 5, 1)


def test_generate_slug_normalizes_chinese_and_special():
    assert generate_slug(["memory allocator", "CXL/分级内存"]) == "memory-allocator-cxl"
    # default cap is 4 keywords
    assert generate_slug(["x"] * 10) == "x-x-x-x"
    # custom cap honored
    assert generate_slug(["x"] * 10, max_words=6) == "x-x-x-x-x-x"


def test_generate_slug_window_label():
    from scripts.input_parser import window_label
    assert window_label("last 6 months") == "6mo"
    assert window_label("Q1 2026") == "Q1-2026"
    assert window_label("2025-11-01..2026-05-01") == "2025-11-2026-05"


def test_parse_time_window_chinese_year(monkeypatch):
    from datetime import date
    monkeypatch.setattr("scripts.input_parser._today", lambda: date(2026, 5, 22))
    start, end = parse_time_window("近 1 年")
    assert end == date(2026, 5, 22)
    assert start == date(2025, 5, 22)


def test_parse_time_window_chinese_months_no_space(monkeypatch):
    from datetime import date
    monkeypatch.setattr("scripts.input_parser._today", lambda: date(2026, 5, 22))
    start, end = parse_time_window("近6个月")
    assert end == date(2026, 5, 22)
    assert start == date(2025, 11, 22)


def test_parse_time_window_chinese_weeks(monkeypatch):
    from datetime import date
    monkeypatch.setattr("scripts.input_parser._today", lambda: date(2026, 5, 22))
    start, end = parse_time_window("近 2 周")
    assert end == date(2026, 5, 22)
    assert start == date(2026, 5, 8)


def test_parse_time_window_chinese_days(monkeypatch):
    from datetime import date
    monkeypatch.setattr("scripts.input_parser._today", lambda: date(2026, 5, 22))
    start, end = parse_time_window("近 30 天")
    assert end == date(2026, 5, 22)
    assert start == date(2026, 4, 22)


def test_window_label_chinese():
    from scripts.input_parser import window_label
    assert window_label("近 1 年") == "1y"
    assert window_label("近6个月") == "6mo"
    assert window_label("近 2 周") == "2w"
    assert window_label("近 30 天") == "30d"

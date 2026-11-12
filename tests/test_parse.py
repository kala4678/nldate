"""Behavioral specification for nldate."""

from datetime import date

import pytest

from nldate import parse

TODAY = date(2025, 6, 11)  # Wednesday


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("today", TODAY),
        ("tomorrow", date(2025, 6, 12)),
        ("yesterday", date(2025, 6, 10)),
        ("the day after tomorrow", date(2025, 6, 13)),
        ("day before yesterday", date(2025, 6, 9)),
        ("next Tuesday", date(2025, 6, 17)),
        ("last Wednesday", date(2025, 6, 4)),
        ("next Wednesday", date(2025, 6, 18)),
        ("this Wednesday", TODAY),
        ("Friday", date(2025, 6, 13)),
        ("in 3 days", date(2025, 6, 14)),
        ("two weeks from tomorrow", date(2025, 6, 26)),
        ("3 weeks ago", date(2025, 5, 21)),
        ("1 year and 2 months after yesterday", date(2026, 8, 10)),
        ("5 days before December 1st, 2025", date(2025, 11, 26)),
        ("in twenty-one days", date(2025, 7, 2)),
        ("a month from today", date(2025, 7, 11)),
        ("next year", date(2026, 6, 11)),
        ("last month", date(2025, 5, 11)),
        ("this week", TODAY),
        ("2025-12-01", date(2025, 12, 1)),
        ("2025/12/1", date(2025, 12, 1)),
        ("12/1/2025", date(2025, 12, 1)),
        ("12/1/25", date(2025, 12, 1)),
        ("12/1", date(2025, 12, 1)),
        ("December 1st, 2025", date(2025, 12, 1)),
        ("1 December 2025", date(2025, 12, 1)),
        ("the 1st of December 2025", date(2025, 12, 1)),
        ("Dec. 1", date(2025, 12, 1)),
        ("Monday, December 1, 2025", date(2025, 12, 1)),
        ("  NEXT   tuesday  ", date(2025, 6, 17)),
        ("in 1 year, 2 months and 3 days", date(2026, 8, 14)),
        ("1 week after 2 days before tomorrow", date(2025, 6, 17)),
    ],
)
def test_common_dates(text: str, expected: date) -> None:
    assert parse(text, TODAY) == expected


@pytest.mark.parametrize(
    ("text", "today", "expected"),
    [
        ("in 1 month", date(2025, 1, 31), date(2025, 2, 28)),
        ("in 1 month", date(2024, 1, 31), date(2024, 2, 29)),
        ("1 year after today", date(2024, 2, 29), date(2025, 2, 28)),
        ("1 month ago", date(2025, 3, 31), date(2025, 2, 28)),
        ("tomorrow", date(2025, 12, 31), date(2026, 1, 1)),
        ("yesterday", date(2025, 1, 1), date(2024, 12, 31)),
        ("in 1 month and 1 day", date(2025, 1, 31), date(2025, 3, 1)),
    ],
)
def test_calendar_boundaries(text: str, today: date, expected: date) -> None:
    assert parse(text, today) == expected


@pytest.mark.parametrize(
    "text",
    [
        "",
        " ",
        "pizza",
        "February 30, 2025",
        "2025-02-29",
        "13/1/2025",
        "in cats days",
        "in 3 days garbage",
        "tomorrow please",
        "December 1 2025 extra",
        "before today",
        "in -3 days",
    ],
)
def test_invalid_dates(text: str) -> None:
    with pytest.raises(ValueError):
        parse(text, TODAY)


def test_default_today() -> None:
    before = date.today()
    result = parse("today")
    assert before <= result <= date.today()

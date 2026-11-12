"""Parse common English date expressions without network services."""

import calendar
import re
from datetime import date, timedelta

__all__ = ["parse"]

_MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
_MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})
_MONTHS["sept"] = 9
_WEEKDAYS = {name.lower(): i for i, name in enumerate(calendar.day_name)}
_WEEKDAYS.update({name.lower(): i for i, name in enumerate(calendar.day_abbr)})
_NUMBERS = dict(
    zip(
        [
            "zero",
            "one",
            "two",
            "three",
            "four",
            "five",
            "six",
            "seven",
            "eight",
            "nine",
            "ten",
            "eleven",
            "twelve",
            "thirteen",
            "fourteen",
            "fifteen",
            "sixteen",
            "seventeen",
            "eighteen",
            "nineteen",
        ],
        range(20),
    )
)
_NUMBERS.update(
    {
        "a": 1,
        "an": 1,
        "couple": 2,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }
)


def _number(text: str) -> int:
    if text.isdigit():
        return int(text)
    total = current = 0
    for word in text.replace("-", " ").split():
        if word == "and":
            continue
        if word == "hundred":
            current *= 100
        elif word == "thousand":
            total += current * 1000
            current = 0
        elif word in _NUMBERS:
            current += _NUMBERS[word]
        else:
            raise ValueError(f"Unknown number: {text!r}")
    return total + current


def _offset(text: str) -> tuple[int, int, int]:
    months = days = 0
    pattern = r"([a-z\d -]+?)\s+(years?|months?|weeks?|days?|fortnights?)\b"
    end = 0
    count = 0
    for match in re.finditer(pattern, text):
        if text[end : match.start()].strip(" ,") not in ("", "and"):
            raise ValueError("Invalid duration")
        amount = _number(re.sub(r"^(?:and\s+)", "", match[1].strip()))
        unit = match[2].rstrip("s")
        if unit == "year":
            months += 12 * amount
        elif unit == "month":
            months += amount
        else:
            days += amount * {"day": 1, "week": 7, "fortnight": 14}[unit]
        end = match.end()
        count += 1
    if not count or text[end:].strip():
        raise ValueError("Invalid duration")
    return months, days, count


def _shift(base: date, text: str, sign: int) -> date:
    months, days, _ = _offset(text)
    index = base.year * 12 + base.month - 1 + sign * months
    year, month = divmod(index, 12)
    month += 1
    day = min(base.day, calendar.monthrange(year, month)[1])
    return date(year, month, day) + timedelta(days=sign * days)


def _parse(s: str, today: date) -> date:
    if s in {"today", "now"}:
        return today
    if s in {
        "tomorrow",
        "yesterday",
        "day after tomorrow",
        "the day after tomorrow",
        "day before yesterday",
        "the day before yesterday",
    }:
        return today + timedelta(
            days={"tomorrow": 1, "yesterday": -1}.get(s, 2 if "after" in s else -2)
        )
    match = re.fullmatch(r"(.+?)\s+(before|after|from)\s+(.+)", s)
    if match:
        return _shift(
            _parse(match[3], today), match[1], -1 if match[2] == "before" else 1
        )
    match = re.fullmatch(r"in (.+)|(.+?) (ago|later|hence)", s)
    if match:
        return _shift(today, match[1] or match[2], -1 if match[3] == "ago" else 1)
    match = re.fullmatch(r"(next|last|this) (day|week|month|year)", s)
    if match:
        return _shift(
            today, "1 " + match[2], {"next": 1, "last": -1, "this": 0}[match[1]]
        )
    match = re.fullmatch(r"(?:(next|last|this) )?([a-z]+)", s)
    if match and match[2] in _WEEKDAYS:
        delta = (_WEEKDAYS[match[2]] - today.weekday()) % 7
        if match[1] == "last":
            delta = delta - 7 if delta else -7
        elif match[1] == "next" and delta == 0:
            delta = 7
        return today + timedelta(days=delta)
    match = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", s)
    if match:
        return date(*map(int, match.groups()))
    match = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2}|\d{4}))?", s)
    if match:
        year = int(match[3]) if match[3] else today.year
        if year < 100:
            year += 2000 if year < 69 else 1900
        return date(year, int(match[1]), int(match[2]))
    # Remove a weekday prefix and English ordinal suffixes for named dates.
    s = re.sub(r"^(?:" + "|".join(_WEEKDAYS) + r")\s+", "", s)
    s = re.sub(r"(\d)(?:st|nd|rd|th)\b", r"\1", s)
    s = re.sub(r"\b(?:the|of)\b", " ", s)
    tokens = s.split()
    if len(tokens) in (2, 3):
        if tokens[0] in _MONTHS:
            month, day = _MONTHS[tokens[0]], int(tokens[1])
        elif tokens[1] in _MONTHS:
            month, day = _MONTHS[tokens[1]], int(tokens[0])
        else:
            raise ValueError("Unknown month")
        year = int(tokens[2]) if len(tokens) == 3 else today.year
        return date(year, month, day)
    raise ValueError(f"Unrecognized date: {s!r}")


def parse(s: str, today: date | None = None) -> date:
    """Return the date described by *s* relative to *today*.

    Numeric slash dates use US month/day order. Missing years use today's
    year. Next/last weekdays are strictly future/past. Month and year offsets
    clamp to the last valid day, then apply week and day offsets.
    Unsupported expressions and impossible dates raise ValueError.
    """
    if not isinstance(s, str) or not s.strip():
        raise ValueError("Expected a nonempty date string")
    normalized = " ".join(s.lower().replace(",", " ").replace(".", "").split())
    try:
        return _parse(normalized, today if today is not None else date.today())
    except (ValueError, OverflowError, KeyError) as exc:
        raise ValueError(f"Unrecognized or invalid date: {s!r}") from exc

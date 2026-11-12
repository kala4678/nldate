# nldate

A small, deterministic Python package for parsing common English dates. No API
keys, network requests, or runtime dependencies are needed.

```python
from datetime import date
from nldate import parse

parse("5 days before December 1st, 2025")  # date(2025, 11, 26)
parse("two weeks from tomorrow", today=date(2025, 6, 11))  # date(2025, 6, 26)
parse("1 year and 2 months after yesterday", today=date(2025, 6, 11))
# date(2026, 8, 10)
```

## Development

Created with `uv init --package nldate`. Install [uv](https://docs.astral.sh/uv/),
then run these commands from the repository root:

```sh
uv sync --locked
uv run pytest
uv run mypy src/
uv run ruff check
uv run ruff format --check
```

## Supported expressions

- `today`, `now`, `tomorrow`, `yesterday`, `the day after tomorrow`, and
  `the day before yesterday`.
- Weekday names and abbreviations, optionally prefixed by `next`, `last`, or
  `this`: `next Tuesday`, `last Wed`, `Friday`.
- Durations: `in 3 days`, `two weeks ago`, `a month from today`,
  `1 year and 2 months after yesterday`, `5 days before December 1st, 2025`.
  Units are days, weeks, fortnights, months, and years; numbers may be digits
  or English words. Durations may be combined and reference dates nested.
- `next`, `last`, or `this` day, week, month, or year.
- ISO-style dates: `2025-12-01`, `2025/12/1`.
- US numeric dates: `12/1/2025`, `12-1-2025`, `12/1/25`, `12/1`.
- Named dates: `December 1st, 2025`, `1 December 2025`,
  `the 1st of December 2025`, `Dec. 1`, `Monday, December 1, 2025`.

Input is case insensitive; extra spaces and commas are accepted. Empty,
unsupported, and impossible dates raise `ValueError`.

## Date conventions

`today` defaults to `datetime.date.today()`. Pass it explicitly for reproducible
results. Missing years use the reference year. Numeric dates use month/day
order; two-digit years 00–68 mean 2000–2068 and 69–99 mean 1969–1999.

`next` and `last` weekdays are strictly future and past; bare and `this`
weekdays mean the next occurrence including today. `next week` means seven days
from today. Calendar offsets apply combined years and months first, clamping
the day to the destination month's last day, then apply weeks and days.
For example, one month after January 31, 2025 is February 28, 2025.
A weekday prefix on an absolute date is informational.

The repository's tests specify the supported behavior. The course autograder
suite was not supplied, so passing these tests does not establish that every
course test will pass.

"""Validate overflow options and render a bounded integer template."""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from string import Formatter
from typing import TypeAlias
from unicodedata import decimal

More: TypeAlias = str | Callable[[int], object]
_MESSAGE = "more may only use the field {n}, with format width and precision at most 10000"


def _render(template: str, count: int) -> str:
    try:
        for _, field, spec, _ in Formatter().parse(template):
            if field is None:
                continue
            spec = spec or ""
            if field != "n" or "{" in spec or "}" in spec:
                raise ValueError(_MESSAGE)
            for digits in re.findall(r"\d+", spec):
                number = 0
                for digit in digits:
                    number = number * 10 + decimal(digit)
                    if number > 10000:
                        raise ValueError(_MESSAGE)
        return template.format(n=count)
    except (ValueError, TypeError, KeyError, IndexError, AttributeError, OverflowError):
        raise ValueError(_MESSAGE) from None


def truncate(items: Iterable[object], limit: int | None, more: More) -> list[str]:
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an int or None")
        limit = int.__int__(limit)
        if limit < 0:
            raise ValueError("limit must not be negative")
    if not isinstance(more, str) and not callable(more):
        raise TypeError("more must be a str or a callable")
    if isinstance(more, str):
        more = str.__str__(more)
    parts = [str(item) for item in items]
    if limit is None or len(parts) <= limit:
        return parts
    hidden = len(parts) - limit
    tail = _render(more, hidden) if isinstance(more, str) else str(more(hidden))
    return [*parts[:limit], tail]

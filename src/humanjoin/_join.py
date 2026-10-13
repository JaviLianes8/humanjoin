"""Join lists of strings into English phrases with a chosen conjunction."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeAlias

__all__ = ["More", "join", "join_max", "truncate"]

# The tail that replaces hidden items: a template with ``{n}`` or a callable taking ``n``.
More: TypeAlias = str | Callable[[int], object]


def truncate(items: Iterable[object], limit: int | None, more: More) -> list[str]:
    """``items`` as strings, keeping at most ``limit`` and appending the tail for the rest."""
    parts = [str(item) for item in items]
    if limit is None:
        return parts
    if isinstance(limit, bool) or not isinstance(limit, int):
        raise TypeError(f"limit must be an int or None, not {type(limit).__name__}")
    if limit < 0:
        raise ValueError(f"limit must not be negative, got {limit}")
    hidden = len(parts) - limit
    if hidden <= 0:
        return parts
    if isinstance(more, str):
        tail = more.format(n=hidden)
    elif callable(more):
        tail = str(more(hidden))
    else:
        raise TypeError(f"more must be a str or a callable, not {type(more).__name__}")
    return [*parts[:limit], tail]


def join(items: Iterable[object], *, conj: str = "and", oxford: bool = True) -> str:
    """Join items into a phrase like ``a, b, and c``.

    Zero items give an empty string, one gives the item alone, two are joined by the
    conjunction without a comma, and three or more use commas with an optional Oxford
    comma before the final conjunction. Items are coerced to strings. For other languages
    and list types use :func:`format_list`.
    """
    if not isinstance(conj, str):
        raise TypeError(f"conj must be a str, not {type(conj).__name__}")
    parts = [str(item) for item in items]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} {conj} {parts[1]}"
    head = ", ".join(parts[:-1])
    separator = f", {conj} " if oxford else f" {conj} "
    return f"{head}{separator}{parts[-1]}"


def join_max(
    items: Iterable[object],
    limit: int,
    *,
    more: More = "{n} more",
    conj: str = "and",
    oxford: bool = True,
) -> str:
    """Join items, keeping at most ``limit`` of them and folding the rest into a tail.

    With five items and a limit of two the result is ``a, b, and 3 more``. The tail comes
    from ``more``: a template that receives the hidden count as ``n``, or a callable that
    takes the count, for plurals. ``conj`` and ``oxford`` are passed on to :func:`join`.
    When nothing is hidden the result is identical to :func:`join`. A negative limit
    raises ``ValueError``.
    """
    if limit is None:
        raise TypeError("limit must be an int, not None")
    return join(truncate(items, limit, more), conj=conj, oxford=oxford)

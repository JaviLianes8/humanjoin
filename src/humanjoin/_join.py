"""Join lists of strings into natural-language phrases."""

from __future__ import annotations

from collections.abc import Iterable

__all__ = ["join", "join_max"]


def join(items: Iterable[object], *, conj: str = "and", oxford: bool = True) -> str:
    """Join items into a phrase like ``a, b, and c``.

    Zero items give an empty string, one gives the item alone, two are joined by the
    conjunction without a comma, and three or more use commas with an optional Oxford
    comma before the final conjunction. Items are coerced to strings.
    """
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


def join_max(items: Iterable[object], limit: int, *, more: str = "{n} more") -> str:
    """Join items, keeping at most ``limit`` of them and folding the rest into a tail.

    With five items and a limit of two the result is ``a, b, and 3 more``. The tail is
    rendered from the ``more`` template, which receives the remaining count as ``n``.
    When nothing is truncated the result is identical to :func:`join`.
    """
    parts = [str(item) for item in items]
    shown = parts if limit >= len(parts) else parts[: max(limit, 0)]
    remaining = len(parts) - len(shown)
    if remaining > 0:
        shown = [*shown, more.format(n=remaining)]
    return join(shown)

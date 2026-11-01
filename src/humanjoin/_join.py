"""Join lists of strings into English phrases with a chosen conjunction."""

from __future__ import annotations

from collections.abc import Iterable

from ._options import text_option
from ._tail import More, truncate

__all__ = ["join", "join_max"]


def _options(conj: str, oxford: bool) -> str:
    conj = text_option(conj, "conj")
    if type(oxford) is not bool:
        raise TypeError("oxford must be a bool")
    return conj


def join(items: Iterable[object], *, conj: str = "and", oxford: bool = True) -> str:
    """Join items into a phrase like ``a, b, and c``.

    Zero items give an empty string, one gives the item alone, two are joined by the
    conjunction without a comma, and three or more use commas with an optional Oxford
    comma before the final conjunction. Items are coerced to strings. For other languages
    and list types use :func:`format_list`.

    >>> join(["a", "b", "c"])
    'a, b, and c'
    >>> join([1, 2, 3], conj="or", oxford=False)
    '1, 2 or 3'
    """
    conj = _options(conj, oxford)
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

    >>> join_max(["a", "b", "c", "d"], 2)
    'a, b, and 2 more'
    """
    if limit is None:
        raise TypeError("limit must be an int, not None")
    conj = _options(conj, oxford)
    return join(truncate(items, limit, more), conj=conj, oxford=oxford)

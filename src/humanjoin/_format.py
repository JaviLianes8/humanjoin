"""Locale-aware list formatting with the vocabulary of ``Intl.ListFormat``."""

from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache
from typing import Literal, TypeAlias, get_args

from ._join import More, truncate
from ._locale import resolve_locale, table
from ._pattern import ListPattern

__all__ = ["ListStyle", "ListType", "format_list", "list_pattern"]

ListType: TypeAlias = Literal["conjunction", "disjunction", "unit"]
ListStyle: TypeAlias = Literal["long", "short", "narrow"]

_TYPES: tuple[str, ...] = get_args(ListType)
_STYLES: tuple[str, ...] = get_args(ListStyle)


@lru_cache(maxsize=512)
def _pattern(locale: str, kind: str, style: str) -> ListPattern:
    if kind not in _TYPES:
        raise ValueError(f"type must be one of {', '.join(_TYPES)}, not {kind!r}")
    if style not in _STYLES:
        raise ValueError(f"style must be one of {', '.join(_STYLES)}, not {style!r}")
    resolved = resolve_locale(locale)
    data = table()
    index = data["locales"][resolved][_TYPES.index(kind) * 3 + _STYLES.index(style)]
    two, start, middle, end = data["patterns"][index]
    return ListPattern(two, start, middle, end, language=resolved.split("-")[0])


def list_pattern(
    locale: str = "en", type: ListType = "conjunction", style: ListStyle = "long"
) -> ListPattern:
    """The CLDR list pattern of ``locale`` for a list ``type`` and ``style``.

    ``type`` is ``conjunction`` ("a, b, and c"), ``disjunction`` ("a, b, or c") or ``unit``
    ("3 ft, 7 in"); ``style`` is ``long``, ``short`` or ``narrow``, as in
    ``Intl.ListFormat``. Raises ``ValueError`` for another type or style and
    ``LookupError`` for a locale without data (see :func:`resolve_locale`).
    """
    for name, value in (("locale", locale), ("type", type), ("style", style)):
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a str, not {value.__class__.__name__}")
    return _pattern(locale, type, style)


def format_list(
    items: Iterable[object],
    locale: str = "en",
    *,
    type: ListType = "conjunction",
    style: ListStyle = "long",
    limit: int | None = None,
    more: More = "{n} more",
) -> str:
    """Join ``items`` the way ``locale`` writes a list, following Unicode CLDR.

    ``format_list(["a", "b", "c"], "de")`` is ``a, b und c``. Items are converted with
    ``str``. With ``limit`` at most that many items are shown and the rest become one last
    item made from ``more``: a template with ``{n}`` or a callable taking the hidden count.
    The default ``more`` is English; pass your own for another language.
    """
    pattern = list_pattern(locale, type, style)
    return pattern.format(truncate(items, limit, more))

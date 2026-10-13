"""Join a list into a natural-language phrase: Oxford comma, overflow limit, CLDR locales."""

from __future__ import annotations

from ._format import ListStyle, ListType, format_list, list_pattern
from ._join import join, join_max
from ._locale import cldr_version, resolve_locale, supported_locales
from ._pattern import ListPattern

__version__ = "0.2.0"

__all__ = [
    "ListPattern",
    "ListStyle",
    "ListType",
    "cldr_version",
    "format_list",
    "join",
    "join_max",
    "list_pattern",
    "resolve_locale",
    "supported_locales",
]

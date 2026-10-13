"""Locale lookup in the pattern table derived from Unicode CLDR."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib.resources import files
from typing import Any

__all__ = ["cldr_version", "resolve_locale", "supported_locales", "table"]

_SUBTAG = re.compile(r"[A-Za-z0-9]{1,8}")
_LANGUAGE = re.compile(r"[A-Za-z]{2,3}|[A-Za-z]{5,8}")


@lru_cache(maxsize=1)
def table() -> dict[str, Any]:
    """The pattern table shipped with the package (see scripts/build_patterns.py)."""
    text = files("humanjoin").joinpath("_cldr.json").read_text(encoding="ascii")
    loaded: dict[str, Any] = json.loads(text)
    return loaded


def cldr_version() -> str:
    """The CLDR release the pattern table was derived from."""
    return str(table()["cldr"])


def supported_locales() -> tuple[str, ...]:
    """Every CLDR locale with list patterns, sorted; ``und`` is the root locale."""
    return tuple(sorted(table()["locales"]))


def _parse(locale: str) -> list[str]:
    """Language, optional script and optional region of a BCP 47 or POSIX locale tag."""
    if not isinstance(locale, str):
        raise TypeError(f"locale must be a str, not {type(locale).__name__}")
    tag = locale.split(".", 1)[0].split("@", 1)[0]  # POSIX "es_ES.UTF-8@euro"
    subtags = tag.replace("_", "-").split("-")
    if subtags[0].lower() == "root":
        subtags[0] = "und"
    if not all(_SUBTAG.fullmatch(part) for part in subtags) or not _LANGUAGE.fullmatch(subtags[0]):
        raise ValueError(f"not a locale tag: {locale!r}")
    language = subtags[0].lower()
    language = table()["aliases"].get(language, language)
    parts = [language]
    rest = subtags[1:]
    if rest and len(rest[0]) == 4 and rest[0].isalpha():
        parts.append(rest.pop(0).title())
    if rest and (
        (len(rest[0]) == 2 and rest[0].isalpha()) or (len(rest[0]) == 3 and rest[0].isdigit())
    ):
        parts.append(rest[0].upper())
    # Variants, extensions and private use do not select list patterns: they are ignored.
    return parts


def resolve_locale(locale: str) -> str:
    """The CLDR locale whose list patterns ``locale`` uses.

    Accepts BCP 47 (``pt-BR``) and POSIX (``pt_BR.UTF-8``) spellings in any case. Deprecated
    language codes are replaced (``iw`` is ``he``), a region implies its likely script where
    the language is written in several (``zh-TW`` is ``zh-Hant-TW``), and a locale without
    data of its own falls back through the CLDR parent locales, then by dropping subtags
    (``en-IN`` reads ``en-001``, ``de-AT-1996`` reads ``de-AT``). ``und`` and ``root`` name
    the root locale. Raises ``LookupError`` when no language with data is reached, so an
    unknown language never reads another language's patterns silently.
    """
    data = table()
    parts = _parse(locale)
    if len(parts) == 2 and len(parts[1]) != 4:
        script = data["scripts"].get(f"{parts[0]}-{parts[1]}")
        if script:
            parts.insert(1, script)
    tag = "-".join(parts)
    while tag:
        if tag in data["locales"]:
            return tag
        parent = data["parents"].get(tag)
        if parent is not None:
            tag = "und" if parent == "root" else parent
        else:
            tag = tag.rpartition("-")[0]
    raise LookupError(f"no list patterns for locale {locale!r}")

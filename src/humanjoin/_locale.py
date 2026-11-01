"""Locale lookup in the pattern table derived from Unicode CLDR."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from ._locale_tag import parse

__all__ = ["cldr_version", "resolve_locale", "supported_locales", "table"]


@lru_cache(maxsize=1)
def table() -> dict[str, Any]:
    """The pattern table shipped with the package (see scripts/build_patterns.py)."""
    text = files("humanjoin").joinpath("_cldr.json").read_text(encoding="ascii")
    loaded: dict[str, Any] = json.loads(text)
    return loaded


def cldr_version() -> str:
    """The CLDR release the pattern table was derived from.

    >>> cldr_version()
    '48.0.0'
    """
    return str(table()["cldr"])


def supported_locales() -> tuple[str, ...]:
    """Every CLDR locale with list patterns, sorted; ``und`` is the root locale.

    >>> len(supported_locales())
    766
    >>> 'und' in supported_locales()
    True
    """
    return tuple(sorted(table()["locales"]))


def _walk(tag: str) -> str | None:
    """The first locale with data on the CLDR fallback chain of ``tag``."""
    data = table()
    while tag:
        if tag in data["locales"]:
            return tag
        parent = data["parents"].get(tag)  # CLDR JSON names the root locale "und"
        language, _, script = tag.partition("-")
        default = data["scripts"].get(language)
        if (
            parent is None
            and len(script) == 4
            and script.isalpha()
            and default
            and script != default
        ):
            parent = data["nonlikelyScript"]
        tag = parent if parent is not None else tag.rpartition("-")[0]
    return None


def resolve_locale(locale: str) -> str:
    """The CLDR locale whose list patterns ``locale`` uses.

    Accepts BCP 47 (``pt-BR``) and POSIX (``pt_BR.UTF-8``, ``sr_RS@latin``) spellings in any
    case. Deprecated codes are replaced (``iw`` is ``he``, ``sh`` is ``sr-Latn``, ``UK`` is
    ``GB``), and where a language is written in several scripts the likely one is added
    (``zh-TW`` reads ``zh-Hant``, ``zh-SG`` reads ``zh-Hans-SG``). A locale without data of its
    own falls back through the CLDR parent locales, then by dropping subtags (``pt-FR``
    reads ``pt-PT``, ``de-AT-1996`` reads ``de-AT``).
    Compound aliases such as ``no-nynorsk`` select ``nn``. Default-script removal retains
    variants. Nonlikely scripts without their own data inherit root (``ru-Latn`` is ``und``).
    ``und`` and ``root`` name the root locale.
    Raises ``LookupError`` when no language with data is reached, so an unknown language
    never reads another language's patterns silently.

    >>> resolve_locale("pt_BR.UTF-8")
    'pt'
    >>> resolve_locale("zh-TW")
    'zh-Hant'
    """
    data = table()
    language, script, region, variants = parse(locale, data)
    base = "-".join(part for part in (language, script, region) if part)
    full = "-".join([base, *variants])
    if full in data["locales"]:
        return full
    if base in data["locales"]:
        return base
    found = None
    default = data["scripts"].get(language)
    if script and script == default:  # "en-Latn-GB" is "en-GB": CLDR omits default scripts
        base = "-".join(part for part in (language, region) if part)
        full = "-".join([base, *variants])
    elif not script and default:
        likely = data["scripts"].get(f"{language}-{region}", default)
        tagged = "-".join(part for part in (language, likely, region, *variants) if part)
        if likely != default:
            found = _walk(tagged)
        elif tagged in data["locales"]:
            found = tagged
    found = found or _walk(full)
    if found is None:
        raise LookupError("no list patterns for locale")
    return found

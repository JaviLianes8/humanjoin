"""Locale lookup in the pattern table derived from Unicode CLDR."""

from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files
from typing import Any

from ._locale_tag import _fields, parse

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


def _variant_match(tag: str) -> str | None:
    locales = table()["locales"]
    if tag in locales:
        return tag
    language, script, region, variants = _fields(tag.split("-"))
    base = "-".join(part for part in (language, script, region) if part)
    if variants:
        wanted = set(variants)
        candidates: list[str] = []
        # Search only available combinations: enumerating all subsets would be exponential.
        for candidate in locales:
            if not candidate.startswith(base + "-"):
                continue
            fields = _fields(candidate.split("-"))
            if fields[:3] == (language, script, region) and set(fields[3]) <= wanted:
                candidates.append(candidate)
        if candidates:
            return min(candidates, key=lambda value: (-value.count("-"), value))
    return base if base in locales else None


def _walk(tag: str) -> str | None:
    """The first locale with data on the CLDR fallback chain of ``tag``."""
    data = table()
    while tag:
        found = _variant_match(tag)
        if found:
            return found
        language, script, region, variants = _fields(tag.split("-"))
        parent = data["parents"].get(tag)  # CLDR JSON names the root locale "und"
        if parent is None and variants:
            tag = "-".join(part for part in (language, script, region) if part)
            continue
        default = data["scripts"].get(language)
        if parent is None and script and script == default:
            # Missing default-script entries still inherit the scriptless regional parent.
            tag = "-".join(part for part in (language, region) if part)
            continue
        if parent is None and script and not region and default and script != default:
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
    Alias chains such as ``nor-nynorsk`` select ``nn``. Available variant combinations
    precede the base locale (``be-tarask-fonipa`` reads ``be-tarask``). Script normalization
    retains variants; unsupported variants still reach regional data (``zh-SG-1996`` reads
    ``zh-Hans-SG``). Nonlikely scripts without data inherit root (``ru-Latn`` is ``und``).
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
    direct = _variant_match(full)
    if direct:
        return direct
    found = None
    default = data["scripts"].get(language)
    if script and script == default:  # "en-Latn-GB" is "en-GB": CLDR omits default scripts
        base = "-".join(part for part in (language, region) if part)
        full = "-".join([base, *variants])
    elif not script and default:
        likely = data["scripts"].get(f"{language}-{region}", default)
        tagged = "-".join(part for part in (language, likely, region, *variants) if part)
        found = _walk(tagged)
    found = found or _walk(full)
    if found is None:
        raise LookupError("no list patterns for locale")
    return found

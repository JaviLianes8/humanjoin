"""CLDR 48 alias facts fetched on 2026-11-01; suffix probes are hand-written.

https://registry.npmjs.org/cldr-core/-/cldr-core-48.0.0.tgz
https://www.unicode.org/reports/tr35/tr35-77/tr35.html#LocaleId_Canonicalization
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from humanjoin import format_list, list_pattern, resolve_locale, supported_locales


@pytest.mark.parametrize(
    ("locale", "canonical"),
    [
        ("en-200", "en-CZ"),
        ("en-582", "en-FM"),
        ("en-830", "en-JE"),
        ("en-PC", "en-FM"),
        ("kk-SU", "kk-KZ"),
        ("nl-AN", "nl-CW"),
        ("sk-200", "sk-SK"),
        ("cnr-YU", "sr-RS"),
        ("kaz-SU", "kk-KZ"),
    ],
)
def test_territory_aliases_select_likely_or_first_replacement(locale: str, canonical: str) -> None:
    assert resolve_locale(locale) == resolve_locale(canonical)
    assert list_pattern(locale) == list_pattern(canonical)
    assert format_list("ABC", locale) == format_list("ABC", canonical)
    if locale.startswith("en-"):
        assert format_list("ABC", locale) == "A, B and C"


@pytest.mark.parametrize("function", [resolve_locale, list_pattern, format_list])
@pytest.mark.parametrize(
    ("locale", "canonical"),
    [("zh-hakka", "hak"), ("zh-xiang", "hsn"), ("hy-arevmda", "hyw")],
)
@pytest.mark.parametrize("suffix", ["", "-fonipa"])
def test_unavailable_canonical_languages_raise_for_deprecated_spellings(
    function: Callable[..., object], locale: str, canonical: str, suffix: str
) -> None:
    for tag in (canonical, locale):
        args = ("ABC",) if function is format_list else ()
        with pytest.raises(LookupError, match=r"^no list patterns for locale$"):
            function(*args, locale=tag + suffix)


def test_supported_locales_returns_an_immutable_tuple() -> None:
    assert isinstance(supported_locales(), tuple)


@pytest.mark.parametrize("singleton", ["u", "x"])
@pytest.mark.parametrize(("base", "variant"), [("ca-ES", "valencia"), ("be", "tarask")])
def test_extension_payloads_cannot_select_available_variants(
    singleton: str, base: str, variant: str
) -> None:
    assert resolve_locale(f"{base}-{variant}") != resolve_locale(base)
    locale = f"{base}-{singleton}-{variant}"
    assert resolve_locale(locale) == resolve_locale(base)
    assert list_pattern(locale) == list_pattern(base)
    assert format_list("ABC", locale) == format_list("ABC", base)

"""Locale resolution, list_pattern and format_list.

Expected phrases are CLDR 48 list patterns; test_sources.py and test_intl.py check the
whole table against the CLDR files and Intl.ListFormat.
"""

from __future__ import annotations

import pytest

from humanjoin import (
    ListPattern,
    cldr_version,
    format_list,
    list_pattern,
    resolve_locale,
    supported_locales,
)


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("en", "en"),
        ("EN-us", "en"),
        ("en_IN.UTF-8", "en-IN"),
        ("en-ZZ", "en"),
        ("en-Cyrl", "en"),
        ("de-AT-1996", "de-AT"),
        ("de-CH-u-co-phonebk", "de-CH"),
        ("de-x-private", "de"),
        ("es_ES@euro", "es"),
        ("zh", "zh"),
        ("zh-TW", "zh-Hant"),
        ("zh-hant-hk", "zh-Hant-HK"),
        ("sr-ME", "sr-Latn-ME"),
        ("sr-RS", "sr"),
        ("pa-PK", "pa-Arab"),
        ("iw", "he"),
        ("tl-PH", "fil"),
        ("eng", "en"),
        ("es-419", "es-419"),
        ("es-AR", "es-AR"),
        ("pt-AO", "pt-AO"),
        ("root", "und"),
        ("und-FR", "und"),
    ],
)
def test_resolve_locale(tag: str, expected: str) -> None:
    assert resolve_locale(tag) == expected


def test_a_parent_locale_is_followed_before_truncation() -> None:
    # pt-FR has no data of its own; CLDR makes pt-PT its parent, which differs from pt.
    assert "pt-FR" not in supported_locales()
    assert resolve_locale("pt-FR") == "pt-PT"
    assert format_list("abc", "pt-FR", type="unit", style="narrow") == "a, b e c"
    assert format_list("abc", "pt", type="unit", style="narrow") == "a b c"
    assert resolve_locale("es-JP") == "es-419"
    assert resolve_locale("ky-Latn") == "und"


def test_parent_root_reads_the_root_patterns() -> None:
    assert format_list("abc", "und") == "a, b, c"


@pytest.mark.parametrize("tag", ["xx", "qaa-FR", "abcde"])
def test_an_unknown_language_raises_lookup_error(tag: str) -> None:
    with pytest.raises(LookupError, match=tag):
        resolve_locale(tag)


@pytest.mark.parametrize("tag", ["", "e", "en--US", "en US", "1234", "en-toolongsubtag", "é"])
def test_a_malformed_tag_raises_value_error(tag: str) -> None:
    with pytest.raises(ValueError, match="locale"):
        resolve_locale(tag)


def test_a_locale_that_is_not_text_raises_type_error() -> None:
    with pytest.raises(TypeError, match="locale"):
        resolve_locale(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="locale"):
        format_list("ab", ["en"])  # type: ignore[arg-type]


def test_supported_locales_and_version() -> None:
    locales = supported_locales()
    assert len(locales) == 766
    assert list(locales) == sorted(locales)
    assert {"en", "und", "zh-Hant", "sr-Latn-ME", "es-419"} <= set(locales)
    assert cldr_version() == "48.0.0"


@pytest.mark.parametrize(
    ("args", "expected"),
    [
        (("en", "conjunction", "long"), "a, b, and c"),
        (("en", "conjunction", "short"), "a, b, & c"),
        (("en", "conjunction", "narrow"), "a, b, c"),
        (("en", "disjunction", "long"), "a, b, or c"),
        (("en", "unit", "long"), "a, b, c"),
        (("en", "unit", "narrow"), "a b c"),
        (("en-GB", "conjunction", "long"), "a, b and c"),
        (("de", "conjunction", "long"), "a, b und c"),
        (("fr", "disjunction", "long"), "a, b ou c"),
        (("ja", "conjunction", "long"), "a、b、c"),
        (("es", "conjunction", "long"), "a, b y c"),
    ],
)
def test_format_list_uses_the_cldr_patterns(args: tuple[str, str, str], expected: str) -> None:
    locale, kind, style = args
    assert format_list("abc", locale, type=kind, style=style) == expected  # type: ignore[arg-type]


def test_list_pattern_returns_the_patterns_and_the_language() -> None:
    assert list_pattern("en") == ListPattern(
        "{0} and {1}", "{0}, {1}", "{0}, {1}", "{0}, and {1}", language="en"
    )
    assert list_pattern("es-MX", "disjunction").language == "es"
    assert list_pattern("iw").language == "he"


def test_format_list_defaults_to_english_conjunction_long() -> None:
    assert format_list(["a", "b"]) == "a and b"


def test_format_list_applies_contextual_rules_through_the_locale() -> None:
    assert format_list(["agua", "hielo"], "es") == "agua y hielo"
    assert format_list(["padre", "hijo"], "es-MX") == "padre e hijo"
    assert format_list(["siete", "ocho"], "es", type="disjunction") == "siete u ocho"


@pytest.mark.parametrize(("kind", "style"), [("and", "long"), ("conjunction", "wide"), ("", "")])
def test_unknown_type_or_style_raises_value_error(kind: str, style: str) -> None:
    with pytest.raises(ValueError, match=r"type|style"):
        format_list("ab", "en", type=kind, style=style)  # type: ignore[arg-type]


def test_type_and_style_must_be_text() -> None:
    with pytest.raises(TypeError, match="style"):
        list_pattern("en", "unit", 1)  # type: ignore[arg-type]


def test_format_list_truncates_with_a_localised_tail() -> None:
    items = ["a", "b", "c", "d"]
    assert format_list(items, "en", limit=2) == "a, b, and 2 more"
    assert format_list(items, "de", limit=2, more="{n} weitere") == "a, b und 2 weitere"
    assert format_list(items, "fr", limit=1, more=lambda n: f"{n} autres") == "a et 3 autres"
    assert format_list(items, "de", limit=4) == "a, b, c und d"


def test_format_list_rejects_a_negative_limit() -> None:
    with pytest.raises(ValueError, match="limit"):
        format_list("abc", "en", limit=-2)

"""Hand-written cases derived from CLDR 48 sources fetched on 2026-11-01.

https://registry.npmjs.org/cldr-core/-/cldr-core-48.0.0.tgz
https://registry.npmjs.org/cldr-misc-full/-/cldr-misc-full-48.0.0.tgz
https://www.unicode.org/reports/tr35/tr35-76/tr35.html#LocaleId_Canonicalization
https://www.unicode.org/reports/tr35/tr35-76/tr35.html#Locale_Inheritance
"""

from __future__ import annotations

import pytest

from humanjoin import format_list, resolve_locale
from humanjoin._locale import table


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("nor-nynorsk", "nn"),
        ("nor-bokmal", "nb"),
        ("aar-saaho", "ssy"),
        ("NOR_Latn_NO_NYNORSK.UTF-8", "nn"),
        ("nor-Cyrl-NO-nynorsk", "und"),
        ("nor-nynorsk-u-nu-latn", "nn"),
    ],
)
def test_alias_rules_repeat_in_field_precedence_order(locale: str, expected: str) -> None:
    assert resolve_locale(locale) == expected


def test_chained_alias_selects_nynorsk_unit_patterns() -> None:
    assert format_list(["A", "B", "C"], "nor-nynorsk", type="unit", style="narrow") == "A B C"


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("en-nynorsk", "en"),
        ("en-bokmal", "en"),
        ("en-saaho", "en"),
        ("en-lojban", "en"),
        ("sv-aaland", "sv-AX"),
    ],
)
def test_compound_alias_requires_its_source_language(locale: str, expected: str) -> None:
    assert resolve_locale(locale) == expected


@pytest.mark.parametrize("locale", ["cat-ES-valencia", "cat-Latn-ES-valencia", "bel-tarask"])
def test_language_alias_preserves_unrelated_variants(locale: str) -> None:
    expected = "be-tarask" if locale.startswith("bel") else "ca-ES-valencia"
    assert resolve_locale(locale) == expected


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("be-tarask-fonipa", "be-tarask"),
        ("be-fonipa-tarask", "be-tarask"),
        ("be-Cyrl-tarask-fonipa", "be-tarask"),
        ("ca-ES-fonipa-valencia", "ca-ES-valencia"),
        ("ca-ES-valencia-fonipa", "ca-ES-valencia"),
        ("ca-Latn-ES-fonipa-valencia", "ca-ES-valencia"),
        ("ca-Latn-ES-valencia-fonipa", "ca-ES-valencia"),
        ("el-polyton-fonipa", "el-polyton"),
        ("ca-ES-fonipa", "ca"),
    ],
)
def test_variant_combinations_precede_base_fallback(locale: str, expected: str) -> None:
    assert resolve_locale(locale) == expected


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("zh-SG-fonipa", "zh-Hans-SG"),
        ("zh-SG-1996", "zh-Hans-SG"),
        ("zh-SG-1996-fonipa", "zh-Hans-SG"),
        ("zh-TW-fonipa", "zh-Hant"),
        ("zh-TW-1996", "zh-Hant"),
        ("sr-RS-fonipa", "sr"),
        ("pt-FR-fonipa", "pt-PT"),
    ],
)
def test_unavailable_variants_keep_likely_script_region(locale: str, expected: str) -> None:
    assert resolve_locale(locale) == expected


def test_likely_script_preserves_available_variant_data(monkeypatch: pytest.MonkeyPatch) -> None:
    # Synthetic data makes premature variant removal observable independently of CLDR coverage.
    locales = table()["locales"]
    monkeypatch.setitem(locales, "zh-Hans-SG-1996", locales["zh-Hans-SG"])
    assert resolve_locale("zh-SG-1996") == "zh-Hans-SG-1996"


def test_variant_fallback_orders_by_count_then_alphabetically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Synthetic entries distinguish the ordering where shipped data has only one variant per base.
    locales = table()["locales"]
    for tag in ("en-fonipa", "en-scouse", "en-fonipa-scouse"):
        monkeypatch.setitem(locales, tag, locales["en"])
    assert resolve_locale("en-scouse-1996-fonipa") == "en-fonipa-scouse"
    monkeypatch.delitem(locales, "en-fonipa-scouse")
    assert resolve_locale("en-scouse-1996-fonipa") == "en-fonipa"


def test_many_unavailable_variants_retain_supported_variant() -> None:
    suffixes = [f"v{index:04d}" for index in range(38)]
    assert resolve_locale("-".join(["be", "tarask", *suffixes])) == "be-tarask"

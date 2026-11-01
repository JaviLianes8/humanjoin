"""Locale contracts derived from CLDR 48 facts fetched on 2026-11-01.

Sources: https://registry.npmjs.org/cldr-core/-/cldr-core-48.0.0.tgz
https://registry.npmjs.org/cldr-misc-full/-/cldr-misc-full-48.0.0.tgz
https://www.unicode.org/reports/tr35/tr35-76/tr35.html#Parent_Locales
Additional suffix combinations below are hand-written cases.
"""

from __future__ import annotations

import pytest

from humanjoin import format_list, resolve_locale


@pytest.mark.parametrize(
    ("locale", "expected"),
    [
        ("aa-saaho", "ssy"),
        ("art-lojban", "jbo"),
        ("no-bokmal", "nb"),
        ("no-nynorsk", "nn"),
        ("NO_Latn_NO_NYNORSK.UTF-8", "nn"),
        ("no-nynorsk-u-nu-latn", "nn"),
        ("no-Cyrl-NO-nynorsk", "und"),
        ("sh-Cyrl-RS", "sr"),
        ("cnr-RS", "sr"),
    ],
)
def test_compound_aliases_preserve_explicit_fields(locale: str, expected: str) -> None:
    assert resolve_locale(locale) == expected


def test_compound_alias_selects_nynorsk_unit_patterns() -> None:
    assert format_list(["A", "B", "C"], "no-nynorsk", type="unit", style="narrow") == "A B C"


@pytest.mark.parametrize("locale", ["ca-Latn-ES-valencia", "ca_ES_valencia@latin"])
def test_default_script_normalization_preserves_variant(locale: str) -> None:
    assert resolve_locale(locale) == "ca-ES-valencia"


@pytest.mark.parametrize("locale", ["ru-Latn", "de-Arab", "en-Cyrl", "fr-Cyrl", "ru-Latn-RU"])
def test_nonlikely_script_inherits_root(locale: str) -> None:
    assert resolve_locale(locale) == "und"
    assert format_list(["A", "B", "C"], locale) == "A, B, C"


@pytest.mark.parametrize("locale", ["xx-Latn", "qaa-Cyrl-RU", "abcde-Arab"])
def test_unknown_languages_with_scripts_still_raise(locale: str) -> None:
    with pytest.raises(LookupError):
        resolve_locale(locale)


@pytest.mark.parametrize("locale", ["de-1996", "ru-1901", "de-Latn-1996", "ru-Cyrl-1901"])
def test_numeric_variants_are_not_treated_as_scripts(locale: str) -> None:
    assert resolve_locale(locale) == locale.split("-")[0]

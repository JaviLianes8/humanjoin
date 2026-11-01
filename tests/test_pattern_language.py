"""Hand-written contracts: custom language codes select contextual rules exactly."""

from __future__ import annotations

import pytest

from humanjoin import ListPattern


class _Text(str):
    def __str__(self) -> str:
        raise AssertionError("option conversion must use the underlying string")


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    ("language", "field", "last", "expected"),
    [
        ("es", "{0} y {1}", "hijo", "a e hijo"),
        ("ES", "{0} y {1}", "hijo", "a y hijo"),
        ("Es", "{0} y {1}", "hijo", "a y hijo"),
        ("eS", "{0} y {1}", "hijo", "a y hijo"),
        ("es", "{0} o {1}", "ocho", "a u ocho"),
        ("ES", "{0} o {1}", "ocho", "a o ocho"),
        ("Es", "{0} o {1}", "ocho", "a o ocho"),
        ("eS", "{0} o {1}", "ocho", "a o ocho"),
        ("he", "{0} \u05d5{1}", "B", "a \u05d5-B"),
        ("HE", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("He", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("hE", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("iw", "{0} \u05d5{1}", "B", "a \u05d5-B"),
        ("IW", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("Iw", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("iW", "{0} \u05d5{1}", "B", "a \u05d5B"),
    ],
)
def test_custom_language_preserves_case_and_selects_exact_contextual_rules(
    text_type: type[str], language: str, field: str, last: str, expected: str
) -> None:
    pattern = ListPattern(field, "{0}+{1}", "{0}+{1}", field, language=text_type(language))
    assert pattern.language == language
    assert type(pattern.language) is str
    assert pattern.format(["a", last]) == expected
    assert pattern.format(["x", "a", last]) == "x+" + expected


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("separator", ["-", "_"])
@pytest.mark.parametrize("suffix", ["region", "script", "script_region"])
@pytest.mark.parametrize(
    ("base", "region", "script", "field", "last", "expected"),
    [
        ("es", "ES", "Latn", "{0} y {1}", "hijo", "a y hijo"),
        ("es", "ES", "Latn", "{0} o {1}", "ocho", "a o ocho"),
        ("he", "IL", "Hebr", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("iw", "IL", "Hebr", "{0} \u05d5{1}", "B", "a \u05d5B"),
    ],
)
def test_custom_language_subtags_stay_literal_without_contextual_rules(
    text_type: type[str],
    separator: str,
    suffix: str,
    base: str,
    region: str,
    script: str,
    field: str,
    last: str,
    expected: str,
) -> None:
    subtags = {"region": [region], "script": [script], "script_region": [script, region]}
    language = separator.join([base, *subtags[suffix]])
    pattern = ListPattern(field, "{0}+{1}", "{0}+{1}", field, language=text_type(language))
    assert pattern.language == language
    assert type(pattern.language) is str
    assert pattern.format(["a", last]) == expected
    assert pattern.format(["x", "a", last]) == "x+" + expected


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    ("field", "last", "expected"),
    [
        ("{0} y {1}", "hijo", "a y hijo"),
        ("{0} o {1}", "ocho", "a o ocho"),
        ("{0} \u05d5{1}", "B", "a \u05d5B"),
    ],
)
def test_empty_custom_language_remains_a_string_distinct_from_none(
    text_type: type[str], field: str, last: str, expected: str
) -> None:
    empty = ListPattern(field, "{0}+{1}", "{0}+{1}", field, language=text_type(""))
    absent = ListPattern(field, "{0}+{1}", "{0}+{1}", field, language=None)
    assert empty.language == ""
    assert type(empty.language) is str
    assert absent.language is None
    assert empty != absent
    assert empty.format(["a", last]) == absent.format(["a", last]) == expected
    assert empty.format(["x", "a", last]) == "x+" + expected

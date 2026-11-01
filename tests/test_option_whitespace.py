"""Hand-written contracts: text normalization preserves significant whitespace."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import pytest

from humanjoin import ListPattern, join, join_max


class _Text(str):
    def __str__(self) -> str:
        raise AssertionError("option conversion must use the underlying string")


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("function", [join, join_max])
@pytest.mark.parametrize(
    ("conj", "pair", "oxford", "no_oxford"),
    [
        (" and ", "a  and  b", "a, b,  and  c", "a, b  and  c"),
        ("\tand\n", "a \tand\n b", "a, b, \tand\n c", "a, b \tand\n c"),
        ("\u00a0", "a \u00a0 b", "a, b, \u00a0 c", "a, b \u00a0 c"),
    ],
)
def test_joiners_preserve_conjunction_whitespace(
    text_type: type[str],
    function: Callable[..., str],
    conj: str,
    pair: str,
    oxford: str,
    no_oxford: str,
) -> None:
    options = {"limit": 3} if function is join_max else {}
    assert function("ab", conj=text_type(conj), **options) == pair
    assert function("abc", conj=text_type(conj), **options) == oxford
    assert function("abc", conj=text_type(conj), oxford=False, **options) == no_oxford


@pytest.mark.parametrize("text_type", [str, _Text])
def test_overflow_preserves_conjunction_whitespace(text_type: type[str]) -> None:
    assert join_max("abc", 1, conj=text_type(" and ")) == "a  and  2 more"
    assert join_max("abcd", 2, conj=text_type(" and ")) == "a, b,  and  2 more"


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    ("field", "items", "expected"),
    [
        ("two", "ab", " \ta+b\n\u00a0"),
        ("start", "abc", " \ta+b\n\u00a0+c"),
        ("middle", "abcd", " \ta+b+c\n\u00a0+d"),
        ("middle", "abcde", " \t \ta+b+c\n\u00a0+d\n\u00a0+e"),
        ("end", "abc", " \ta+b+c\n\u00a0"),
    ],
)
def test_custom_pattern_fields_preserve_whitespace(
    text_type: type[str], field: str, items: str, expected: str
) -> None:
    plain = ListPattern("{0}+{1}", "{0}+{1}", "{0}+{1}", "{0}+{1}")
    value = " \t{0}+{1}\n\u00a0"
    pattern = replace(plain, **{field: text_type(value)})
    assert pattern.format(items) == expected
    assert getattr(pattern, field) == value
    assert type(getattr(pattern, field)) is str


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(("prefix", "suffix"), [(" ", ""), ("", " "), ("\t", "\n\u00a0")])
@pytest.mark.parametrize(
    ("language", "field", "last", "expected"),
    [
        ("es", "{0} y {1}", "hijo", "a y hijo"),
        ("es", "{0} o {1}", "ocho", "a o ocho"),
        ("he", "{0} \u05d5{1}", "B", "a \u05d5B"),
        ("iw", "{0} \u05d5{1}", "B", "a \u05d5B"),
    ],
)
def test_padded_language_values_keep_patterns_literal(
    text_type: type[str],
    prefix: str,
    suffix: str,
    language: str,
    field: str,
    last: str,
    expected: str,
) -> None:
    value = prefix + language + suffix
    pattern = ListPattern(field, "{0}+{1}", "{0}+{1}", field, language=text_type(value))
    assert pattern.format(["a", last]) == expected
    assert pattern.format(["x", "a", last]) == "x+" + expected
    assert pattern.language == value
    assert type(pattern.language) is str

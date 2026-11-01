"""Hand-written contracts: text options preserve exact Unicode code points."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

import pytest

from humanjoin import ListPattern, format_list, join, join_max


class _Text(str):
    def __str__(self) -> str:
        raise AssertionError("option conversion must use the underlying string")


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("function", [join, join_max])
@pytest.mark.parametrize(
    ("conj", "pair", "oxford", "no_oxford"),
    [
        ("\r\n", "a \r\n b", "a, b, \r\n c", "a, b \r\n c"),
        ("e\u0301", "a e\u0301 b", "a, b, e\u0301 c", "a, b e\u0301 c"),
        ("x\x00y", "a x\x00y b", "a, b, x\x00y c", "a, b x\x00y c"),
        ("\ufeffand", "a \ufeffand b", "a, b, \ufeffand c", "a, b \ufeffand c"),
    ],
)
def test_joiners_preserve_conjunction_code_points(
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
@pytest.mark.parametrize(
    ("conj", "pair", "oxford", "no_oxford"),
    [
        ("\r\n", "a \r\n 2 more", "a, b, \r\n 2 more", "a, b \r\n 2 more"),
        ("e\u0301", "a e\u0301 2 more", "a, b, e\u0301 2 more", "a, b e\u0301 2 more"),
        ("x\x00y", "a x\x00y 2 more", "a, b, x\x00y 2 more", "a, b x\x00y 2 more"),
        ("\ufeffand", "a \ufeffand 2 more", "a, b, \ufeffand 2 more", "a, b \ufeffand 2 more"),
    ],
)
def test_overflow_preserves_conjunction_code_points(
    text_type: type[str], conj: str, pair: str, oxford: str, no_oxford: str
) -> None:
    assert join_max("abc", 1, conj=text_type(conj)) == pair
    assert join_max("abcd", 2, conj=text_type(conj)) == oxford
    assert join_max("abcd", 2, conj=text_type(conj), oxford=False) == no_oxford


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize(
    ("more", "expected"),
    [
        ("\r\n{n}\r\n", "\r\n2\r\n"),
        ("e\u0301{n}", "e\u03012"),
        ("x\x00{n}y", "x\x002y"),
        ("\ufeff{n} more", "\ufeff2 more"),
    ],
)
def test_overflow_templates_preserve_code_points(
    text_type: type[str], function: Callable[..., str], more: str, expected: str
) -> None:
    assert function("ab", limit=0, more=text_type(more)) == expected
    assert function("abc", limit=1, more=text_type(more)) == "a and " + expected


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("literal", ["\r\n", "e\u0301", "x\x00y", "\ufeff"])
@pytest.mark.parametrize(
    ("field", "items", "expected"),
    [
        ("two", "ab", "{s}a+b{s}"),
        ("start", "abc", "{s}a+b{s}+c"),
        ("middle", "abcd", "{s}a+b+c{s}+d"),
        ("middle", "abcde", "{s}{s}a+b+c{s}+d{s}+e"),
        ("end", "abc", "{s}a+b+c{s}"),
    ],
)
def test_custom_pattern_fields_preserve_code_points(
    text_type: type[str], literal: str, field: str, items: str, expected: str
) -> None:
    plain = ListPattern("{0}+{1}", "{0}+{1}", "{0}+{1}", "{0}+{1}")
    value = literal + "{0}+{1}" + literal
    pattern = replace(plain, **{field: text_type(value)})
    assert pattern.format(items) == expected.format(s=literal)
    assert getattr(pattern, field) == value
    assert type(getattr(pattern, field)) is str


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("language", ["\r\n", "e\u0301", "e\x00s", "\ufeffes"])
def test_custom_language_preserves_code_points(text_type: type[str], language: str) -> None:
    field = "{0} y {1}"
    pattern = ListPattern(field, field, field, field, language=text_type(language))
    assert pattern.language == language
    assert type(pattern.language) is str
    assert pattern.format(["padre", "hijo"]) == "padre y hijo"

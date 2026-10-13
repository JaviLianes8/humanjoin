"""ListPattern: validation, the formatting algorithm and the contextual rules.

Expected values here are written by hand from the algorithm; the same behaviour is also
checked against Intl.ListFormat output in test_intl.py.
"""

from __future__ import annotations

import dataclasses

import pytest

from humanjoin import ListPattern

VAV = chr(0x05D5)
ENGLISH = ListPattern("{0} and {1}", "{0}, {1}", "{0}, {1}", "{0}, and {1}")


@pytest.mark.parametrize(
    ("count", "expected"),
    [(0, ""), (1, "a"), (2, "a and b"), (3, "a, b, and c"), (5, "a, b, c, d, and e")],
)
def test_each_list_length_uses_its_pattern(count: int, expected: str) -> None:
    assert ENGLISH.format("abcde"[:count]) == expected


def test_start_middle_and_end_are_applied_left_to_right() -> None:
    marked = ListPattern("{0} 2 {1}", "{0} S {1}", "{0} M {1}", "{0} E {1}")
    assert marked.format("abcde") == "a S b M c M d E e"
    assert marked.format("abc") == "a S b E c"
    assert marked.format("ab") == "a 2 b"


def test_text_after_the_last_item_is_kept_once_per_pattern() -> None:
    suffixed = ListPattern("{0}, {1} R", "{0}, {1}", "{0}, {1}", "{0}, {1} R")
    assert suffixed.format("abc") == "a, b, c R"


def test_text_before_the_first_item_wraps_the_text_so_far() -> None:
    prefixed = ListPattern("({0} {1})", "<{0} {1}", "{0} {1}", "{0} {1}>")
    assert prefixed.format("ab") == "(a b)"
    assert prefixed.format("abc") == "<a b c>"


def test_a_pattern_may_put_the_new_item_first() -> None:
    reversed_two = ListPattern("{1} after {0}", "{0}, {1}", "{0}, {1}", "{1} after {0}")
    assert reversed_two.format("ab") == "b after a"
    assert reversed_two.format("abc") == "c after a, b"


def test_braces_inside_items_are_not_substituted() -> None:
    assert ENGLISH.format(["{1}", "{0}", "{1}"]) == "{1}, {0}, and {1}"


def test_items_are_converted_with_str() -> None:
    assert ENGLISH.format([1, None, 2.5]) == "1, None, and 2.5"


@pytest.mark.parametrize("field", ["two", "start", "middle", "end"])
@pytest.mark.parametrize("bad", ["{0} and", "{1}", "{0} {0} {1}", "{0}{1}{1}", "a"])
def test_each_pattern_needs_both_placeholders_exactly_once(field: str, bad: str) -> None:
    with pytest.raises(ValueError, match=field):
        dataclasses.replace(ENGLISH, **{field: bad})


def test_patterns_must_be_text() -> None:
    with pytest.raises(TypeError, match="middle"):
        ListPattern("{0} {1}", "{0} {1}", None, "{0} {1}")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="language"):
        ListPattern("{0} {1}", "{0} {1}", "{0} {1}", "{0} {1}", language=1)  # type: ignore[arg-type]


def test_the_pattern_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        ENGLISH.two = "{0} or {1}"  # type: ignore[misc]


SPANISH_AND = ListPattern("{0} y {1}", "{0}, {1}", "{0}, {1}", "{0} y {1}", language="es")
SPANISH_OR = ListPattern("{0} o {1}", "{0}, {1}", "{0}, {1}", "{0} o {1}", language="es")


@pytest.mark.parametrize("word", ["i", "Ida", "hijo", "Hilo", "hI", "hi", "hio", "hiu"])
def test_spanish_and_becomes_e_before_an_i_sound(word: str) -> None:
    assert SPANISH_AND.format(["a", word]) == f"a e {word}"
    assert SPANISH_AND.format(["a", "b", word]) == f"a, b e {word}"


@pytest.mark.parametrize("word", ["hielo", "hiato", "HIE", "hIa", "h", "", "Ícaro", " i", "y"])
def test_spanish_and_stays_y_otherwise(word: str) -> None:
    assert SPANISH_AND.format(["a", word]) == f"a y {word}"


@pytest.mark.parametrize("word", ["o", "Olga", "hoja", "HO", "8", "80", "11", "11 años"])
def test_spanish_or_becomes_u_before_an_o_sound(word: str) -> None:
    assert SPANISH_OR.format(["a", word]) == f"a u {word}"
    assert SPANISH_OR.format(["a", "b", word]) == f"a, b u {word}"


@pytest.mark.parametrize("word", ["110", "11a", "1", "uva", "h", "", "Óscar"])
def test_spanish_or_stays_o_otherwise(word: str) -> None:
    assert SPANISH_OR.format(["a", word]) == f"a o {word}"


def test_spanish_rules_need_the_spanish_language() -> None:
    plain = dataclasses.replace(SPANISH_AND, language=None)
    assert plain.format(["a", "hijo"]) == "a y hijo"
    assert dataclasses.replace(SPANISH_OR, language="pt").format(["a", "ola"]) == "a o ola"


def test_spanish_rules_only_touch_the_exact_patterns() -> None:
    other = ListPattern("{0} y {1}", "{0}, {1}", "{0}, {1}", "{0}, y {1}", language="es")
    assert other.format(["a", "b", "hijo"]) == "a, b, y hijo"
    assert other.format(["a", "hijo"]) == "a e hijo"


HEBREW = ListPattern(f"{{0}} {VAV}{{1}}", "{0}, {1}", "{0}, {1}", f"{{0}} {VAV}{{1}}", "he")


@pytest.mark.parametrize("word", ["ABC", "1", "-x", " " + chr(0x05D0), chr(0x1F600)])
def test_hebrew_and_takes_a_hyphen_before_another_script(word: str) -> None:
    assert HEBREW.format(["a", word]) == f"a {VAV}-{word}"
    assert HEBREW.format(["a", "b", word]) == f"a, b {VAV}-{word}"


@pytest.mark.parametrize("point", [0x0591, 0x05BE, 0x05C7, 0x05D0, 0x05EA, 0x05EF, 0xFB1D, 0xFB4F])
def test_hebrew_and_joins_a_hebrew_word_directly(point: int) -> None:
    assert HEBREW.format(["a", chr(point)]) == f"a {VAV}{chr(point)}"


@pytest.mark.parametrize("point", [0x0590, 0x05C8, 0x05EB, 0x05F5, 0xFB37, 0xFB50])
def test_hebrew_range_edges_are_exact(point: int) -> None:
    assert HEBREW.format(["a", chr(point)]) == f"a {VAV}-{chr(point)}"


def test_hebrew_rule_accepts_the_old_language_code_and_skips_empty_items() -> None:
    assert dataclasses.replace(HEBREW, language="iw").format(["a", "B"]) == f"a {VAV}-B"
    assert HEBREW.format(["a", ""]) == f"a {VAV}"

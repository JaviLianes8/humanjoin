"""Hand-written contracts: option subclasses use their underlying built-in values."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import NoReturn

import pytest

from humanjoin import ListPattern, format_list, join, join_max, list_pattern, resolve_locale


def _hook(*args: object, **kwargs: object) -> NoReturn:
    raise RuntimeError("option hook must not run")


class _Text(str):
    __str__ = _hook
    __len__ = _hook
    __hash__ = _hook
    __eq__ = _hook
    __format__ = _hook
    __getitem__ = _hook
    __contains__ = _hook
    partition = _hook
    split = _hook
    count = _hook
    format = _hook


class _Integer(int):
    __int__ = _hook
    __index__ = _hook
    __lt__ = _hook
    __ge__ = _hook
    __rsub__ = _hook


class _Negative(int):
    def __lt__(self, other: object) -> bool:
        return False


class _ClassPropertyInteger(int):
    __class__ = property(_hook)


def _untouched() -> Iterator[str]:
    raise AssertionError("invalid options must not consume items")
    yield "unused"


@pytest.mark.parametrize("function", [join_max, format_list])
def test_negative_subclass_limit_is_rejected_before_iteration(function: Callable[..., str]) -> None:
    with pytest.raises(ValueError, match="negative"):
        function(_untouched(), limit=_Negative(-1))


@pytest.mark.parametrize("function", [join_max, format_list])
def test_integer_options_ignore_overridden_operations(function: Callable[..., str]) -> None:
    assert function("abc", limit=_Integer(1)) == "a and 2 more"


@pytest.mark.parametrize("function", [join_max, format_list])
def test_integer_validation_does_not_read_class_property(function: Callable[..., str]) -> None:
    with pytest.raises(ValueError, match=r"^limit must not be negative$"):
        function(_untouched(), limit=_ClassPropertyInteger(-1))
    assert function("abc", limit=_ClassPropertyInteger(1)) == "a and 2 more"


@pytest.mark.parametrize("function", [resolve_locale, list_pattern])
def test_locale_subclasses_are_normalized_before_bounds_and_caching(
    function: Callable[..., object],
) -> None:
    assert function(_Text("en")) == function("en")
    with pytest.raises(ValueError, match="255"):
        function(_Text("en@" + "x" * 253))


def test_list_type_and_style_subclasses_use_underlying_values() -> None:
    assert list_pattern("en", _Text("unit"), _Text("narrow")).format("abc") == "a b c"  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="type"):
        list_pattern("en", _Text("invalid"))  # type: ignore[arg-type]


@pytest.mark.parametrize("function", [join, join_max])
def test_conjunction_subclasses_use_underlying_text(function: Callable[..., str]) -> None:
    options = {"limit": 3} if function is join_max else {}
    assert function("ab", conj=_Text("or"), **options) == "a or b"


@pytest.mark.parametrize("function", [join_max, format_list])
def test_template_subclasses_do_not_override_formatting(function: Callable[..., str]) -> None:
    assert function([1], limit=0, more=_Text("{n}")) == "1"
    with pytest.raises(ValueError, match="at most 10000"):
        function([1], limit=0, more=_Text("{n:10001}"))


def test_pattern_fields_and_language_are_normalized_before_validation() -> None:
    field = _Text("{0} y {1}")
    pattern = ListPattern(field, field, field, field, language=_Text("es"))
    assert pattern.format(["padre", "hijo"]) == "padre e hijo"
    plain = "{0} y {1}"
    assert hash(pattern) == hash(ListPattern(plain, plain, plain, plain, "es"))
    assert type(pattern.two) is str and type(pattern.language) is str
    with pytest.raises(ValueError, match="exactly once"):
        ListPattern(*[_Text("{0}{0}{1}")] * 4)

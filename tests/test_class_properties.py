"""Hand-written contracts: invalid options cannot invoke class-property hooks."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import NoReturn

import pytest

from humanjoin import ListPattern, format_list, join, join_max, list_pattern, resolve_locale


class _ClassProperty:
    class_reads = 0

    def _read_class(self) -> NoReturn:
        self.class_reads += 1
        raise RuntimeError("private option hook")

    __class__ = property(_read_class)


class _Bytes(_ClassProperty, bytes):
    pass


def _untouched() -> Iterator[str]:
    raise AssertionError("invalid options must not consume items")
    yield "unused"


@pytest.mark.parametrize(
    ("function", "option"),
    [
        (resolve_locale, "locale"),
        (list_pattern, "locale"),
        (list_pattern, "type"),
        (list_pattern, "style"),
        (format_list, "locale"),
        (format_list, "type"),
        (format_list, "style"),
        (join, "conj"),
        (join_max, "conj"),
        (ListPattern, "two"),
        (ListPattern, "start"),
        (ListPattern, "middle"),
        (ListPattern, "end"),
        (ListPattern, "language"),
    ],
)
def test_text_options_reject_bytes_without_reading_class_property(
    function: Callable[..., object], option: str
) -> None:
    value = _Bytes(b"en")
    options: dict[str, object] = {}
    if function is ListPattern:
        options.update(dict.fromkeys(("two", "start", "middle", "end"), "{0} and {1}"))
    if function is join_max:
        options["limit"] = 1
    options[option] = value
    args = (_untouched(),) if function in (join, join_max, format_list) else ()
    with pytest.raises(TypeError) as caught:
        function(*args, **options)
    assert type(caught.value) is TypeError
    assert str(caught.value) == f"{option} must be a str"
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    assert value.class_reads == 0


@pytest.mark.parametrize("function", [join_max, format_list])
def test_noninteger_limit_is_rejected_without_reading_class_property(
    function: Callable[..., str],
) -> None:
    value = _ClassProperty()
    with pytest.raises(TypeError) as caught:
        function(_untouched(), limit=value)
    assert type(caught.value) is TypeError
    assert str(caught.value) == "limit must be an int or None"
    assert caught.value.__context__ is None
    assert caught.value.__cause__ is None
    assert value.class_reads == 0

"""Hand-written contracts for decimal format bounds and callable tail coercion."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from humanjoin import format_list, join_max


def decimal_text(number: int, alphabet: str) -> str:
    return "".join(alphabet[int(char)] for char in str(number))


@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize(
    "alphabet",
    [
        "0123456789",
        "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669",
        "\uff10\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19",
        "0\u0661\uff123\u0664\uff156\u0667\uff189",
    ],
)
@pytest.mark.parametrize("precision", [False, True])
@pytest.mark.parametrize("bound", [10000, 10001])
def test_decimal_width_and_precision_bounds(
    function: Callable[..., str], alphabet: str, precision: bool, bound: int
) -> None:
    digits = alphabet[0] * 20 + decimal_text(bound, alphabet)
    spec = f".{digits}f" if precision else digits
    template = "{n:" + spec + "}"
    if bound > 10000:
        with pytest.raises(ValueError, match="at most 10000"):
            function([1], limit=0, more=template)
    else:
        expected = "1." + "0" * bound if precision else " " * (bound - 1) + "1"
        # An ASCII leading zero selects zero padding; other zero characters do not.
        if not precision and alphabet[0] == "0":
            expected = "0" * (bound - 1) + "1"
        assert function([1], limit=0, more=template) == expected


@pytest.mark.parametrize("function", [join_max, format_list])
def test_long_unicode_zero_prefix_is_bounded_without_integer_conversion(
    function: Callable[..., str],
) -> None:
    zeros = "\u0660\uff10" * 5000
    assert function([1], limit=0, more="{n:" + zeros + "2}") == " 1"
    with pytest.raises(ValueError, match="at most 10000"):
        function([1], limit=0, more="{n:" + zeros + "\u0661000\uff11}")


@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize("fill", ["\u00b2", "\uff19", "\u0660"])
def test_numeric_fill_characters_remain_literal(function: Callable[..., str], fill: str) -> None:
    assert function([1], limit=0, more="{n:" + fill + ">3}") == fill * 2 + "1"


class _Rendered(str):
    def __str__(self) -> str:
        return "normalized"


class _TailResult:
    def __str__(self) -> str:
        return _Rendered("raw")


@pytest.mark.parametrize("function", [join_max, format_list])
def test_callable_tail_is_stringified_then_coerced_as_an_item(function: Callable[..., str]) -> None:
    counts: list[int] = []

    def tail(count: int) -> object:
        counts.append(count)
        return _TailResult()

    assert function(["item"], limit=0, more=tail) == "normalized"
    assert counts == [1]

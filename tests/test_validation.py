"""Hand-written boundary and error contracts for 1.0.0."""

from __future__ import annotations

import io
from collections.abc import Callable, Iterator

import pytest

from humanjoin import ListPattern, format_list, join, join_max, list_pattern, resolve_locale
from humanjoin._cli import main


@pytest.mark.parametrize("value", [None, 0, 1, "yes", [], object()])
def test_oxford_requires_a_boolean(value: object) -> None:
    with pytest.raises(TypeError, match="oxford"):
        join([], oxford=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("function", [join_max, format_list])
def test_tail_type_is_checked_even_without_overflow(function: Callable[..., str]) -> None:
    with pytest.raises(TypeError, match="more"):
        function([], limit=2, more=object())


@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize("limit", [True, False, 1.0, "1"])
def test_both_truncators_reject_noninteger_limits(
    function: Callable[..., str], limit: object
) -> None:
    with pytest.raises(TypeError, match="limit"):
        function([], limit=limit)


def test_bad_options_do_not_consume_items() -> None:
    def items() -> Iterator[str]:
        raise AssertionError("items must not be consumed")
        yield "unused"

    calls: list[Callable[[], str]] = [
        lambda: join(items(), conj=None),  # type: ignore[arg-type]
        lambda: join_max(items(), -1),
        lambda: join_max(items(), 1, oxford=1),  # type: ignore[arg-type]
        lambda: join_max(items(), 1, conj=None),  # type: ignore[arg-type]
        lambda: format_list(items(), limit=-1),
        lambda: format_list(items(), locale="xx"),
        lambda: format_list(items(), more=42),  # type: ignore[arg-type]
    ]
    for call in calls:
        with pytest.raises((TypeError, ValueError, LookupError)):
            call()


@pytest.mark.parametrize(
    "template",
    [
        "{",
        "}",
        "{n.foo}",
        "{n[0]}",
        "{n:{n}}",
        "{n!x}",
        "{n:10001}",
        "{n:.10001f}",
        "{n:999999999999999999}",
    ],
)
def test_bad_templates_raise_bounded_value_errors_without_context(template: str) -> None:
    with pytest.raises(ValueError) as caught:
        join_max("ab", 1, more=template)
    assert len(str(caught.value)) < 120
    assert caught.value.__suppress_context__


@pytest.mark.parametrize(
    ("template", "tail"),
    [
        ("literal", "literal"),
        ("{{n}} {n:04d}", "{n} 0002"),
        ("{n!r}", "2"),
        ("{n!s:.1}", "2"),
        ("{n!a}", "2"),
        ("{n} {n}", "2 2"),
        ("{n:10000}", " " * 9999 + "2"),
    ],
)
def test_tail_templates_keep_supported_formatting(template: str, tail: str) -> None:
    assert join_max("abc", 1, more=template) == "a and " + tail


def test_no_overflow_skips_template_and_callback() -> None:
    def tail(count: int) -> object:
        raise AssertionError(count)

    for more in ("{bad}", tail):
        assert join_max("ab", 2, more=more) == "a and b"
        assert format_list("ab", limit=None, more=more) == "a and b"


def test_tail_callback_called_once_and_stringified() -> None:
    counts: list[int] = []

    def tail(count: int) -> int:
        counts.append(count)
        return count * 2

    assert join_max("abcd", 1, more=tail) == "a and 6"
    assert counts == [3]


def test_user_exceptions_propagate_unchanged() -> None:
    error = RuntimeError("caller failure")

    def tail(count: int) -> object:
        raise error

    with pytest.raises(RuntimeError) as caught:
        join_max("ab", 0, more=tail)
    assert caught.value is error


def test_locale_length_boundary_is_checked_before_ignored_suffixes() -> None:
    assert resolve_locale("en." + "x" * 252) == "en"
    assert list_pattern("en." + "x" * 252) == list_pattern("en")
    for function in (resolve_locale, list_pattern):
        with pytest.raises(ValueError, match="255"):
            function("en." + "x" * 253)


def test_errors_do_not_echo_long_values_or_type_names() -> None:
    secret = "private-value-" * 10000
    calls: list[Callable[[], object]] = [
        lambda: resolve_locale(secret),
        lambda: list_pattern("en", type=secret),  # type: ignore[arg-type]
        lambda: join_max("ab", -(10**1000)),
        lambda: join_max("ab", 0, more="{" + secret + "}"),
        lambda: ListPattern(secret, "{0}{1}", "{0}{1}", "{0}{1}"),
    ]
    for call in calls:
        with pytest.raises((TypeError, ValueError, LookupError)) as caught:
            call()
        assert "private-value" not in str(caught.value) and len(str(caught.value)) < 150


@pytest.mark.parametrize("flag", ["--limit", "--type", "--style", "--locale"])
def test_cli_errors_do_not_echo_values(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(["a", flag, "secret" * 10000], stdin=io.StringIO(), stdout=io.StringIO())
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert "secret" not in error and len(error) < 1000

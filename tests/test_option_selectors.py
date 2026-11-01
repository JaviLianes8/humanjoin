"""Hand-written contracts: selectors reject padding and require exact type/style case."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

from humanjoin import ListStyle, ListType, format_list, list_pattern, resolve_locale


class _Text(str):
    def __str__(self) -> str:
        raise AssertionError("option conversion must use the underlying string")


class _Untouched:
    def __iter__(self) -> Iterator[str]:
        raise AssertionError("invalid options must be rejected before item iteration")


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    "padding", [(" ", ""), ("", " "), (" ", " "), ("\t", "\r\n"), ("\u00a0", "\u00a0")]
)
@pytest.mark.parametrize("locale", ["en", "en-US"])
@pytest.mark.parametrize("function", [resolve_locale, list_pattern])
def test_locale_lookups_reject_padded_tags(
    text_type: type[str], padding: tuple[str, str], locale: str, function: Callable[..., object]
) -> None:
    function(locale)
    with pytest.raises(ValueError, match="locale"):
        function(text_type(padding[0] + locale + padding[1]))


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    "padding", [(" ", ""), ("", " "), (" ", " "), ("\t", "\r\n"), ("\u00a0", "\u00a0")]
)
@pytest.mark.parametrize("locale", ["en", "en-US"])
def test_format_list_rejects_padded_locale_before_iteration(
    text_type: type[str], padding: tuple[str, str], locale: str
) -> None:
    format_list("ab", locale)
    with pytest.raises(ValueError, match="locale"):
        format_list(_Untouched(), locale=text_type(padding[0] + locale + padding[1]))


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    "padding", [(" ", ""), ("", " "), (" ", " "), ("\t", "\r\n"), ("\u00a0", "\u00a0")]
)
@pytest.mark.parametrize("kind", ["conjunction", "disjunction", "unit"])
@pytest.mark.parametrize("function", [list_pattern, format_list])
def test_list_functions_reject_padded_types(
    text_type: type[str], padding: tuple[str, str], kind: ListType, function: Callable[..., object]
) -> None:
    args = (_Untouched(),) if function is format_list else ()
    list_pattern(type=kind)
    with pytest.raises(ValueError, match="type"):
        function(*args, type=text_type(padding[0] + kind + padding[1]))


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize(
    "padding", [(" ", ""), ("", " "), (" ", " "), ("\t", "\r\n"), ("\u00a0", "\u00a0")]
)
@pytest.mark.parametrize("style", ["long", "short", "narrow"])
@pytest.mark.parametrize("function", [list_pattern, format_list])
def test_list_functions_reject_padded_styles(
    text_type: type[str],
    padding: tuple[str, str],
    style: ListStyle,
    function: Callable[..., object],
) -> None:
    args = (_Untouched(),) if function is format_list else ()
    list_pattern(style=style)
    with pytest.raises(ValueError, match="style"):
        function(*args, style=text_type(padding[0] + style + padding[1]))


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("case", [str.upper, str.title])
@pytest.mark.parametrize("kind", ["conjunction", "disjunction", "unit"])
@pytest.mark.parametrize("function", [list_pattern, format_list])
def test_list_functions_reject_nonlowercase_types(
    text_type: type[str],
    case: Callable[[str], str],
    kind: ListType,
    function: Callable[..., object],
) -> None:
    args = (_Untouched(),) if function is format_list else ()
    list_pattern(type=kind)
    with pytest.raises(ValueError, match=r"^type must be one of conjunction, disjunction, unit$"):
        function(*args, type=text_type(case(kind)))


@pytest.mark.parametrize("text_type", [str, _Text])
@pytest.mark.parametrize("case", [str.upper, str.title])
@pytest.mark.parametrize("style", ["long", "short", "narrow"])
@pytest.mark.parametrize("function", [list_pattern, format_list])
def test_list_functions_reject_nonlowercase_styles(
    text_type: type[str],
    case: Callable[[str], str],
    style: ListStyle,
    function: Callable[..., object],
) -> None:
    args = (_Untouched(),) if function is format_list else ()
    list_pattern(style=style)
    with pytest.raises(ValueError, match=r"^style must be one of long, short, narrow$"):
        function(*args, style=text_type(case(style)))

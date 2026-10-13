from __future__ import annotations

import io

import pytest

from humanjoin import __version__, supported_locales
from humanjoin._cli import main


def run(*argv: str, stdin: str = "") -> tuple[int, str]:
    out = io.StringIO()
    status = main(list(argv), stdin=io.StringIO(stdin), stdout=out)
    return status, out.getvalue()


def test_items_from_arguments_default_to_english() -> None:
    assert run("a", "b", "c") == (0, "a, b, and c\n")


def test_locale_type_and_style_options() -> None:
    assert run("a", "b", "c", "-l", "de") == (0, "a, b und c\n")
    assert run("a", "b", "--locale", "fr", "--type", "disjunction") == (0, "a ou b\n")
    assert run("a", "b", "c", "-t", "unit", "-s", "narrow") == (0, "a b c\n")


def test_items_from_stdin_skip_blank_lines() -> None:
    assert run("-l", "es", stdin="padre\r\n\n  \nhijo\n") == (0, "padre e hijo\n")


def test_limit_and_more() -> None:
    assert run("a", "b", "c", "d", "--limit", "1") == (0, "a and 3 more\n")
    status, out = run("a", "b", "c", "--limit", "1", "--more", "{n} weitere", "-l", "de")
    assert (status, out) == (0, "a und 2 weitere\n")


def test_no_items_print_an_empty_line() -> None:
    assert run() == (0, "\n")


def test_locales_lists_every_supported_locale() -> None:
    status, out = run("--locales")
    assert status == 0
    assert out.splitlines() == list(supported_locales())


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["a", "-l", "xx"], "no list patterns"),
        (["a", "-l", "e"], "not a locale tag"),
        (["a", "b", "--limit", "-1"], "negative"),
        (["a", "b", "--limit", "0", "--more", "{x}"], "error"),
        (["a", "b", "--limit", "0", "--more", "{"], "error"),
    ],
)
def test_bad_values_exit_2_with_a_message(
    argv: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run(*argv)
    assert exit_info.value.code == 2
    assert message in capsys.readouterr().err


def test_an_unknown_type_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run("a", "-t", "and")
    assert exit_info.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run("--version")
    assert exit_info.value.code == 0
    assert capsys.readouterr().out == f"humanjoin {__version__} (CLDR 48.0.0)\n"

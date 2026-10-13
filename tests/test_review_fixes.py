"""Regression tests for the findings of the independent review of the 0.2.0 round."""

from __future__ import annotations

import io

import pytest

from humanjoin import format_list, join_max, resolve_locale, supported_locales
from humanjoin._cli import main


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("sr_RS@latin", "sr-Latn"),
        ("uz_UZ@cyrillic", "uz-Cyrl"),
        ("sr_RS.UTF-8@latin", "sr-Latn"),
        ("sr_RS@euro", "sr"),
        ("sr-Cyrl-RS@latin", "sr"),
    ],
)
def test_posix_script_modifiers_pick_the_script(tag: str, expected: str) -> None:
    assert resolve_locale(tag) == expected


@pytest.mark.parametrize(
    ("tag", "expected"),
    [("sh", "sr-Latn"), ("sh-RS", "sr-Latn"), ("cnr", "sr-Latn-ME"), ("prs", "fa-AF")],
)
def test_language_aliases_keep_their_script_and_region(tag: str, expected: str) -> None:
    assert resolve_locale(tag) == expected


def test_a_given_region_wins_over_the_region_of_an_alias() -> None:
    # Intl.ListFormat of Node 24.18 canonicalises cnr-BA to sr-BA, written in Cyrillic.
    assert resolve_locale("cnr-BA") == "sr-Cyrl-BA"


def test_region_aliases_are_replaced() -> None:
    assert resolve_locale("en-UK") == "en-GB"
    assert format_list("abc", "en-UK") == "a, b and c"


def test_every_supported_locale_resolves_to_itself() -> None:
    for locale in supported_locales():
        assert resolve_locale(locale) == locale


@pytest.mark.parametrize(
    ("tag", "expected"),
    [
        ("zh-SG", "zh-Hans-SG"),
        ("sr-BA", "sr-Cyrl-BA"),
        ("yue-MO", "yue-Hant-MO"),
        ("ca-es-VALENCIA", "ca-ES-valencia"),
        ("en-Latn-GB", "en-GB"),
        ("zh-Hans-CN", "zh"),
    ],
)
def test_default_scripts_and_variants_reach_their_own_locale(tag: str, expected: str) -> None:
    assert resolve_locale(tag) == expected


def test_extended_language_subtags_are_rejected() -> None:
    with pytest.raises(ValueError, match="extended language"):
        resolve_locale("zh-cmn-Hant")


@pytest.mark.parametrize("template", ["{x}", "{0}", "{n.foo}", "{n[0]}"])
def test_a_tail_template_with_another_field_is_a_value_error(template: str) -> None:
    with pytest.raises(ValueError, match="only use the field"):
        join_max(["a", "b", "c"], 1, more=template)


def run(*argv: str, stdin: io.TextIOBase) -> tuple[int, str]:
    out = io.StringIO()
    return main(list(argv), stdin=stdin, stdout=out), out.getvalue()  # type: ignore[arg-type]


def test_stdin_byte_order_mark_and_spaces_are_dropped() -> None:
    text = chr(0xFEFF) + "uno \n  hijo\n"
    assert run("-l", "es", stdin=io.StringIO(text)) == (0, "uno e hijo\n")


def test_stdin_that_is_not_utf8_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    stdin = io.TextIOWrapper(io.BytesIO(b"\xff\n"), encoding="utf-8")
    with pytest.raises(SystemExit) as exit_info:
        run(stdin=stdin)
    assert exit_info.value.code == 2
    assert "not valid UTF-8" in capsys.readouterr().err


class _Terminal(io.StringIO):
    def isatty(self) -> bool:
        return True


def test_no_items_on_a_terminal_is_a_usage_error(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        run(stdin=_Terminal())
    assert exit_info.value.code == 2
    assert "no items" in capsys.readouterr().err


def test_cli_reports_a_bad_tail_template(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        run("a", "b", "--limit", "1", "--more", "{x}", stdin=io.StringIO())
    assert "only use the field {n}" in capsys.readouterr().err

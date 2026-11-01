"""Hand-written subprocess and input-consumption contracts for the command line."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from typing import NoReturn

import pytest

from humanjoin._cli import main


@pytest.mark.parametrize("args", [["--limit", "-1"], ["--locale", "!"], ["--locale", "xx"]])
def test_invalid_cli_options_exit_with_stdin_still_open(args: list[str]) -> None:
    process = subprocess.Popen(
        [sys.executable, "-m", "humanjoin", *args],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        assert process.wait(timeout=5) == 2
        stdout, stderr = process.communicate(timeout=5)
        assert stdout == b"" and b"humanjoin: error:" in stderr
        assert b"Traceback" not in stderr
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)


class _Unread(io.StringIO):
    def __iter__(self) -> NoReturn:
        raise AssertionError("stdin must not be read")


@pytest.mark.parametrize("args", [["--limit", "-1"], ["--locale", "!"], ["--locale", "xx"]])
def test_invalid_cli_options_do_not_read_a_finite_stream(args: list[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main(args, stdin=_Unread("item\n"), stdout=io.StringIO())
    assert caught.value.code == 2


def test_cli_template_validation_still_waits_for_overflow() -> None:
    stdout = io.StringIO()
    assert main(["--more", "{"], stdin=io.StringIO("a\n"), stdout=stdout) == 0
    assert stdout.getvalue() == "a\n"


def test_module_cli_preserves_exact_argument_whitespace() -> None:
    done = subprocess.run(
        [sys.executable, "-m", "humanjoin", " a ", "\tb\t", " c "],
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert done.returncode == 0 and done.stderr == b""
    assert done.stdout == b" a , \tb\t, and  c " + os.linesep.encode()


@pytest.mark.parametrize(
    "digits", ["\u0661\u0660\u0660\u0660", "\uff11\uff10\uff10\uff10", "\u06610\uff100"]
)
@pytest.mark.parametrize("precision", [False, True])
@pytest.mark.parametrize("last", ["0", "1"])
def test_cli_decimal_format_boundaries(digits: str, precision: bool, last: str) -> None:
    spec = f".{digits}{last}f" if precision else digits + last
    done = subprocess.run(
        [sys.executable, "-m", "humanjoin", "item", "--limit", "0", "--more", "{n:" + spec + "}"],
        capture_output=True,
        check=False,
        timeout=30,
    )
    if last == "1":
        assert done.returncode == 2 and done.stdout == b""
        assert b"at most 10000" in done.stderr
    else:
        assert done.returncode == 0 and done.stderr == b""
        expected = b"1." + b"0" * 10000 if precision else b" " * 9999 + b"1"
        assert done.stdout == expected + os.linesep.encode()

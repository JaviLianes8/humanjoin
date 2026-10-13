"""The README examples run and print what they say; docs, versions and files agree."""

from __future__ import annotations

import contextlib
import io
import re
import shlex
from pathlib import Path

import humanjoin
from humanjoin._cli import main

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_every_python_example_prints_its_comments() -> None:
    blocks = re.findall(r"```python\n(.*?)```", README, flags=re.DOTALL)
    assert len(blocks) == 5
    checked = 0
    for block in blocks:
        expected = [line[2:] for line in block.splitlines() if line.startswith("# ")]
        assert expected, block
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            exec(compile(block, "README.md", "exec"), {"__name__": "readme"})
        assert out.getvalue().splitlines() == expected
        checked += len(expected)
    assert checked == 19


def test_every_shell_example_prints_its_output() -> None:
    examples = re.findall(r"^\$ (.+)\n(.+)$", README, flags=re.MULTILINE)
    assert len(examples) == 2
    for command, expected in examples:
        stdin = ""
        if command.startswith("printf "):
            text, command = command.split(" | ", 1)
            stdin = shlex.split(text)[1].replace("\\n", "\n")
        argv = shlex.split(command)
        assert argv[0] == "humanjoin"
        out = io.StringIO()
        assert main(argv[1:], stdin=io.StringIO(stdin), stdout=out) == 0
        assert out.getvalue() == expected + "\n"


def test_the_api_table_lists_every_public_name() -> None:
    table = README.split("## API", 1)[1].split("\n## ", 1)[0]
    for name in humanjoin.__all__:
        assert f"`{name}" in table, name


def test_version_matches_pyproject_and_changelog() -> None:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"$', text, flags=re.MULTILINE)
    assert match is not None and match.group(1) == humanjoin.__version__
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{humanjoin.__version__}]" in changelog


def test_the_unicode_licence_is_shipped_and_declared() -> None:
    licence = (ROOT / "LICENSE-UNICODE").read_text(encoding="utf-8")
    assert licence.startswith("UNICODE LICENSE V3")
    assert licence.rstrip().endswith("SPDX-License-Identifier: Unicode-3.0")
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'license = "MIT AND Unicode-3.0"' in text
    assert '"LICENSE-UNICODE"' in text


def _tracked_text_files() -> list[Path]:
    suffixes = {".py", ".md", ".toml", ".ps1", ".txt", ".yml", ".json", ".mjs"}
    found = []
    for path in ROOT.rglob("*"):
        parts = path.relative_to(ROOT).parts
        if not path.is_file() or path.suffix not in suffixes:
            continue
        if parts[:2] == ("tests", "upstream") and path.name != "MANIFEST.json":
            continue
        if any(
            (part.startswith(".") and part != ".github") or part == "__pycache__" for part in parts
        ):
            continue
        found.append(path)
    return found


def test_no_em_dash_anywhere_in_the_tree() -> None:
    for path in _tracked_text_files():
        assert chr(0x2014) not in path.read_text(encoding="utf-8"), path


def test_source_files_stay_under_two_hundred_lines() -> None:
    for path in _tracked_text_files():
        if path.suffix in {".py", ".mjs", ".ps1"}:
            assert len(path.read_text(encoding="utf-8").splitlines()) <= 200, path

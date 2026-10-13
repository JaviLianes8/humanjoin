"""Build the wheel, install it in a throwaway venv and drive the installed package.

Slow and needs the build backend, so it runs only with HUMANJOIN_E2E=1. Set
HUMANJOIN_E2E_NO_SCRIPT=1 where policy blocks running the generated console script.
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("HUMANJOIN_E2E") != "1", reason="set HUMANJOIN_E2E=1 to build and install"
)

PROGRAM = r"""
import importlib.metadata, importlib.resources
import humanjoin
from humanjoin import (
    ListPattern, cldr_version, format_list, join, join_max, list_pattern, resolve_locale,
    supported_locales,
)

assert "site-packages" in humanjoin.__file__, humanjoin.__file__
assert importlib.metadata.version("humanjoin") == humanjoin.__version__
assert importlib.resources.files("humanjoin").joinpath("py.typed").is_file()
meta = importlib.metadata.metadata("humanjoin")
assert meta["License-Expression"] == "MIT AND Unicode-3.0", meta["License-Expression"]
assert cldr_version() == "48.0.0" and len(supported_locales()) == 766
assert join(["a", "b", "c"], oxford=False) == "a, b and c"
assert join_max("abcde", 2, conj="or") == "a, b, or 3 more"
assert format_list("abc", "de") == "a, b und c"
assert format_list("abc", "zh-TW") == "a" + chr(0x3001) + "b" + chr(0x548C) + "c"
assert format_list(["padre", "hijo"], "es") == "padre e hijo"
assert format_list(["a", "B"], "he") == "a " + chr(0x5D5) + "-B"
assert resolve_locale("pt-FR") == "pt-PT"
english = ListPattern("{0} and {1}", "{0}, {1}", "{0}, {1}", "{0}, and {1}", "en")
assert list_pattern("en") == english
try:
    resolve_locale("xx")
except LookupError:
    pass
else:
    raise AssertionError("expected LookupError")
print("e2e ok")
"""


def _run(
    *cmd: str | Path, cwd: Path | None = None, stdin: bytes = b""
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [str(c) for c in cmd], cwd=cwd, input=stdin, capture_output=True, check=False
    )


def test_installed_wheel_end_to_end(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(sys.executable, "-m", "build", "--outdir", dist, ROOT)
    assert built.returncode == 0, built.stderr
    (wheel,) = dist.glob("humanjoin-*.whl")
    (sdist,) = dist.glob("humanjoin-*.tar.gz")
    names = zipfile.ZipFile(wheel).namelist()
    for name in ("humanjoin/py.typed", "humanjoin/_cldr.json", "humanjoin/__main__.py"):
        assert name in names, name
    licences = {name.rsplit("/", 1)[1] for name in names if "/licenses/" in name}
    assert licences == {"LICENSE", "LICENSE-UNICODE"}
    assert not any(name.startswith(("tests/", "scripts/")) for name in names)
    entry_points = next(name for name in names if name.endswith("entry_points.txt"))
    assert "humanjoin = humanjoin._cli:main" in zipfile.ZipFile(wheel).read(entry_points).decode()
    listing = _run(sys.executable, "-m", "tarfile", "-l", sdist).stdout.decode()
    assert "IMPROVEMENTS-round" not in listing
    for fetched in (".tgz", "Scripts-17", "listformatter", "ecma402", "intl-node"):
        assert fetched not in listing, fetched
    for kept in ("tests/upstream/MANIFEST.json", "scripts/fetch_upstream.py", "LICENSE-UNICODE"):
        assert kept in listing, kept

    env_dir = tmp_path / "venv"
    venv.create(env_dir, with_pip=True)
    bindir = env_dir / ("Scripts" if sys.platform == "win32" else "bin")
    python = bindir / "python"
    installed = _run(python, "-m", "pip", "install", "-q", wheel)
    assert installed.returncode == 0, installed.stderr

    # Run from an empty folder so the source tree cannot shadow the install.
    work = tmp_path / "work"
    work.mkdir()
    result = _run(python, "-I", "-c", PROGRAM, cwd=work)
    assert result.returncode == 0, result.stderr
    assert result.stdout.decode().strip() == "e2e ok"

    script = bindir / ("humanjoin.exe" if sys.platform == "win32" else "humanjoin")
    commands: list[list[str | Path]] = [[python, "-m", "humanjoin"]]
    if os.environ.get("HUMANJOIN_E2E_NO_SCRIPT") != "1":
        commands.append([script])
    for command in commands:
        shown = _run(*command, "-l", "zh-TW", cwd=work, stdin=b"a\nb\n")
        assert shown.returncode == 0, shown.stderr
        assert shown.stdout.decode("utf-8").strip() == "a" + chr(0x548C) + "b"
        failed = _run(*command, "a", "-l", "xx", cwd=work)
        assert failed.returncode == 2 and b"no list patterns" in failed.stderr

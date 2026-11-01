"""Opt-in upgrade using the actual published wheel and a separately built 1.0 wheel."""

from __future__ import annotations

import os
import sys
import venv
from pathlib import Path

import pytest
from test_e2e_wheel import PROGRAM, _run

pytestmark = pytest.mark.skipif(
    os.environ.get("HUMANJOIN_UPGRADE") != "1",
    reason="set HUMANJOIN_UPGRADE=1 and HUMANJOIN_WHEEL to test the live PyPI upgrade",
)

SNAPSHOT = r"""
import hashlib, json, pickle, pathlib
from typing import get_args
import humanjoin as h
outputs = []
for locale in h.supported_locales():
    for kind in get_args(h.ListType):
        for style in get_args(h.ListStyle):
            for count in range(6):
                outputs.append(h.format_list(["a{0}", "b{1}", "hi", "8", "x"][:count],
                    locale, type=kind, style=style))
for limit in range(7):
    outputs.extend(h.join_max("abcde", limit, conj="or", oxford=o) for o in (True, False))
    outputs.append(h.format_list("abcde", "es", limit=limit, more="{n:03d} left"))
print(hashlib.sha256(json.dumps(outputs, ensure_ascii=True).encode()).hexdigest())
pathlib.Path("pattern-" + h.__version__ + ".pickle").write_bytes(pickle.dumps(h.list_pattern("es")))
"""

CHANGES = r"""
import humanjoin as h
old = h.__version__ == "0.2.0"
def raises(kind, call):
    try:
        call()
    except kind:
        return
    raise AssertionError("missing expected error")
if old:
    assert h.join("abc", oxford=1) == "a, b, and c"
    assert h.format_list([], more=42) == ""
    assert h.resolve_locale("en." + "x" * 256) == "en"
    assert h.join_max("ab", 0, more="{n.real}") == "2"
    assert h.join_max("ab", 0, more="{n:10001}") == " " * 10000 + "2"
    assert h.ListPattern.__module__ == "humanjoin._pattern"
else:
    raises(TypeError, lambda: h.join("abc", oxford=1))
    raises(TypeError, lambda: h.format_list([], more=42))
    raises(ValueError, lambda: h.resolve_locale("en." + "x" * 256))
    raises(ValueError, lambda: h.join_max("ab", 0, more="{n.real}"))
    raises(ValueError, lambda: h.join_max("ab", 0, more="{n:10001}"))
    assert h.ListPattern.__module__ == "humanjoin"
for call in (lambda: h.resolve_locale("xx-secret"), lambda: h.join_max("ab", -123456)):
    try:
        call()
    except (ValueError, LookupError) as error:
        assert (("secret" in str(error) or "123456" in str(error)) == old)
    else:
        raise AssertionError("missing expected error")
items = iter("ab")
raises(ValueError, lambda: h.join_max(items, -1))
assert list(items) == ([] if old else ["a", "b"])
assert h.join_max("ab", 2, more="{bad}") == "a and b"
print("documented changes ok")
"""


def test_live_pypi_upgrade_preserves_results_and_pickles(tmp_path: Path) -> None:
    wheel = Path(os.environ["HUMANJOIN_WHEEL"]).resolve()
    assert wheel.name == "humanjoin-1.0.0-py3-none-any.whl" and wheel.is_file()
    bindir = "Scripts" if sys.platform == "win32" else "bin"
    environments = [tmp_path / "published", tmp_path / "upgrade"]
    interpreters = []
    for folder in environments:
        venv.create(folder, with_pip=True)
        python = folder / bindir / "python"
        interpreters.append(python)
        installed = _run(python, "-m", "pip", "install", "--no-deps", "humanjoin==0.2.0")
        assert installed.returncode == 0, installed.stderr
    old, current = interpreters
    work = tmp_path / "consumer"
    work.mkdir()
    before = _run(current, "-I", "-c", SNAPSHOT, cwd=work)
    assert before.returncode == 0, before.stderr
    checked = _run(current, "-I", "-c", CHANGES, cwd=work)
    assert checked.returncode == 0, checked.stderr
    upgraded = _run(current, "-m", "pip", "install", "--no-deps", "--upgrade", wheel)
    assert upgraded.returncode == 0, upgraded.stderr
    after = _run(current, "-I", "-c", SNAPSHOT, cwd=work)
    assert after.returncode == 0, after.stderr
    assert after.stdout == before.stdout
    for program in (PROGRAM, CHANGES):
        checked = _run(current, "-I", "-c", program, cwd=work)
        assert checked.returncode == 0, checked.stderr
    for python, version in ((old, "1.0.0"), (current, "0.2.0")):
        program = (
            "import pathlib, pickle, humanjoin; "
            f"p = pickle.loads(pathlib.Path('pattern-{version}.pickle').read_bytes()); "
            "assert p == humanjoin.list_pattern('es'); "
            "assert p.format(['a', 'hijo']) == 'a e hijo'"
        )
        loaded = _run(python, "-I", "-c", program, cwd=work)
        assert loaded.returncode == 0, loaded.stderr
    script = (
        environments[1] / bindir / ("humanjoin.exe" if sys.platform == "win32" else "humanjoin")
    )
    for command in ([current, "-I", "-m", "humanjoin"], [script]):
        formatted = _run(*command, "a", "b", "c", "--limit", "1", cwd=work)
        assert formatted.returncode == 0 and formatted.stdout.decode().strip() == "a and 2 more"
    clean = _run(current, "-m", "pip", "check")
    assert clean.returncode == 0, clean.stderr

"""Stable signatures, value semantics and executable public documentation."""

from __future__ import annotations

import copy
import doctest
import inspect
import pickle
from pathlib import Path
from typing import Any, get_args, get_type_hints

import pytest

import humanjoin
from humanjoin import ListPattern, ListStyle, ListType, list_pattern


def test_package_namespace_contains_only_the_declared_api() -> None:
    assert {n for n in vars(humanjoin) if not n.startswith("_")} == set(humanjoin.__all__)


@pytest.mark.parametrize(
    ("name", "names", "defaults", "keyword_only"),
    [
        ("join", "items conj oxford", ("and", True), "conj oxford"),
        ("join_max", "items limit more conj oxford", ("{n} more", "and", True), "more conj oxford"),
        (
            "format_list",
            "items locale type style limit more",
            ("en", "conjunction", "long", None, "{n} more"),
            "type style limit more",
        ),
        ("list_pattern", "locale type style", ("en", "conjunction", "long"), ""),
        ("resolve_locale", "locale", (), ""),
        ("supported_locales", "", (), ""),
        ("cldr_version", "", (), ""),
        ("ListPattern", "two start middle end language", (None,), ""),
    ],
)
def test_public_signatures(
    name: str, names: str, defaults: tuple[object, ...], keyword_only: str
) -> None:
    obj = getattr(humanjoin, name)
    parameters = inspect.signature(obj).parameters
    assert list(parameters) == names.split()
    assert tuple(p.default for p in parameters.values() if p.default is not p.empty) == defaults
    for key, parameter in parameters.items():
        expected = (
            parameter.KEYWORD_ONLY
            if key in keyword_only.split()
            else parameter.POSITIONAL_OR_KEYWORD
        )
        assert parameter.kind == expected
    hints = get_type_hints(obj)
    assert hints and all(value is not Any for value in hints.values())


def test_literal_aliases_list_exactly_the_allowed_values() -> None:
    assert get_args(ListType) == ("conjunction", "disjunction", "unit")
    assert get_args(ListStyle) == ("long", "short", "narrow")


@pytest.mark.parametrize("name", humanjoin.__all__)
def test_each_public_docstring_has_passing_examples(name: str) -> None:
    obj = getattr(humanjoin, name)
    doc = inspect.getdoc(obj)
    assert doc and ">>>" in doc
    example = doctest.DocTestParser().get_doctest(doc, vars(humanjoin), name, None, 0)
    result = doctest.DocTestRunner().run(example)
    assert result.failed == 0 and result.attempted > 0


def test_format_method_docstring_runs() -> None:
    doc = inspect.getdoc(ListPattern.format)
    assert doc and ">>>" in doc
    example = doctest.DocTestParser().get_doctest(doc, vars(humanjoin), "format", None, 0)
    result = doctest.DocTestRunner().run(example)
    assert result.failed == 0 and result.attempted > 0


def test_patterns_are_hashable_copyable_public_pickle_values() -> None:
    original = list_pattern("es", "disjunction")
    assert ListPattern.__module__ == "humanjoin"
    for other in (
        copy.copy(original),
        copy.deepcopy(original),
        pickle.loads(pickle.dumps(original)),
    ):
        assert other == original and hash(other) == hash(original)
        assert other.format(["a", "ocho"]) == "a u ocho"
    assert original != list_pattern("en")


def test_readme_links_and_release_metadata() -> None:
    root = Path(__file__).resolve().parents[1]
    readme = (root / "README.md").read_text(encoding="utf-8")
    import re

    assert all(link.startswith("https://") for link in re.findall(r"\]\(([^)]+)\)", readme))
    assert (
        "[![Lianes8 Certified](https://lianes8studio.com/certified/lianes8-certified-badge.svg)](https://lianes8studio.com/certified)"
        in readme
    )
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.0.0"' in project
    assert "Development Status :: 5 - Production/Stable" in project
    assert "dependencies = []" in project
    assert "## [1.0.0] - 2026-11-01" in (root / "CHANGELOG.md").read_text(encoding="utf-8")

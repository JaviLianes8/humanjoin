"""The shipped table and constants agree with the pinned upstream sources.

The sources live in tests/upstream (see MANIFEST.json); these tests skip while absent.
"""

from __future__ import annotations

import importlib.util
import inspect
import io
import json
import re
import tarfile
from pathlib import Path
from types import ModuleType
from typing import Any, get_args

from conftest import read_upstream

from humanjoin import ListStyle, ListType, format_list, list_pattern, supported_locales
from humanjoin._pattern import _HEBREW, _HEBREW_AND, _SPANISH_AND, _SPANISH_OR, _VAV

ROOT = Path(__file__).resolve().parents[1]
CLDR_KEYS = {"conjunction": "standard", "disjunction": "or", "unit": "unit"}


def _build_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "build_patterns", ROOT / "scripts" / "build_patterns.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cldr_list_patterns() -> dict[str, Any]:
    found: dict[str, Any] = {}
    body = read_upstream("cldr-misc-full-48.0.0.tgz")
    with tarfile.open(fileobj=io.BytesIO(body)) as archive:
        for member in archive.getmembers():
            if member.name.endswith("/listPatterns.json"):
                handle = archive.extractfile(member)
                assert handle is not None
                locale = member.name.split("/")[2]
                found[locale] = json.load(handle)["main"][locale]["listPatterns"]
    return found


def test_the_shipped_table_is_a_fresh_derivation_from_cldr() -> None:
    read_upstream("cldr-core-48.0.0.tgz")
    read_upstream("cldr-misc-full-48.0.0.tgz")
    build = _build_script()
    shipped = (ROOT / "src" / "humanjoin" / "_cldr.json").read_text(encoding="ascii")
    assert build.render(build.derive()) == shipped


def test_likely_scripts_keep_only_regions_that_change_the_script() -> None:
    build = _build_script()
    locales = {"zh": [0], "zh-Hant": [0], "en": [0]}
    likely = {
        "zh": "zh-Hans-CN",
        "zh-CN": "zh-Hans-CN",
        "zh-TW": "zh-Hant-TW",
        "zh-Hant": "zh-Hant-TW",
        "en-GB": "en-Latn-GB",
        "en-RU": "en-Cyrl-RU",
    }
    assert build._likely_scripts(locales, likely) == {"zh-TW": "Hant"}


def test_every_locale_type_and_style_reads_its_cldr_patterns() -> None:
    cldr = _cldr_list_patterns()
    assert set(cldr) == set(supported_locales())
    checked = 0
    for locale, sets in cldr.items():
        for kind in get_args(ListType):
            for style in get_args(ListStyle):
                suffix = "" if style == "long" else f"-{style}"
                data = sets[f"listPattern-type-{CLDR_KEYS[kind]}{suffix}"]
                got = list_pattern(locale, kind, style)
                assert (got.two, got.start, got.middle, got.end) == (
                    data["2"],
                    data["start"],
                    data["middle"],
                    data["end"],
                ), (locale, kind, style)
                checked += 1
    assert checked == 766 * 9


def test_the_contextual_patterns_are_the_ones_icu_rewrites() -> None:
    source = read_upstream("icu-78.3-listformatter.cpp").decode("utf-8")
    constants = dict(re.findall(r'const char16_t\* (\w+) = u"([^"]*)";', source))
    assert constants["spanishY"] == _SPANISH_AND
    assert constants["spanishO"] == _SPANISH_OR
    assert constants["spanishE"] == "{0} e {1}"
    assert constants["spanishU"] == "{0} u {1}"
    vav = constants["hebrewVav"].replace("\\u05D5", _VAV)
    assert vav == _HEBREW_AND
    assert constants["hebrewVavDash"].replace("\\u05D5", _VAV) == "{0} " + _VAV + "-{1}"
    assert 'uprv_strcmp(lang, "es") == 0' in source
    assert 'uprv_strcmp(lang, "he") == 0 || uprv_strcmp(lang, "iw") == 0' in source
    assert "!= USCRIPT_HEBREW" in source


def test_the_hebrew_ranges_are_the_hebrew_script_of_unicode_17() -> None:
    text = read_upstream("Scripts-17.0.0.txt").decode("utf-8")
    assert text.startswith("# Scripts-17.0.0.txt")
    ranges: list[list[int]] = []
    for low, high in re.findall(
        r"^([0-9A-F]{4,6})(?:\.\.([0-9A-F]{4,6}))?\s*; Hebrew ", text, re.M
    ):
        start, end = int(low, 16), int(high or low, 16)
        if ranges and ranges[-1][1] == start - 1:
            ranges[-1][1] = end
        else:
            ranges.append([start, end])
    assert [tuple(pair) for pair in ranges] == list(_HEBREW)


def test_types_styles_and_defaults_follow_ecma_402() -> None:
    spec = read_upstream("ecma402-listformat.html").decode("utf-8")

    def option(name: str) -> tuple[list[str], str]:
        match = re.search(
            rf'GetOption\(_options_, \*"{name}"\*, ~string~, « (.*?) », \*"(\w+)"\*\)', spec
        )
        assert match is not None, name
        return re.findall(r'\*"(\w+)"\*', match.group(1)), match.group(2)

    signature = inspect.signature(format_list).parameters
    assert option("type") == (list(get_args(ListType)), signature["type"].default)
    assert option("style") == (list(get_args(ListStyle)), signature["style"].default)
    mapping = re.findall(r'`(\w+)` corresponds to "(\w+)"', spec)
    assert dict(mapping) == CLDR_KEYS

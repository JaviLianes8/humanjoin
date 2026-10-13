"""Output matches Intl.ListFormat of Node 24.18 (ICU 78.3, CLDR 48), recorded in this repo's
tests/upstream/intl-node.json by scripts/intl_reference.mjs.

ICU ships fewer locales than CLDR. Where Intl falls back to another locale (its resolved
locale is neither the requested tag nor the CLDR locale this library resolves to), the case
is skipped: CLDR is the source of truth and test_sources.py covers it.
"""

from __future__ import annotations

from typing import Any

import pytest
from conftest import upstream_json

from humanjoin import format_list, resolve_locale
from humanjoin._pattern import _HEBREW

_SKIPPED_PROBES = {"xx", "en_US"}  # unknown to both, or POSIX spelling Intl rejects


def _comparable(tag: str, resolved: str | None) -> bool:
    if resolved is None:
        return False
    plain = tag.lower().split("-u-")[0].split("-x-")[0]
    try:
        ours = resolve_locale(tag).lower()
    except LookupError:
        return False
    return resolved.lower() in (plain, ours)


@pytest.fixture(scope="module")
def reference() -> Any:
    data = upstream_json("intl-node.json")
    assert (data["icu"], data["cldr"], data["unicode"]) == ("78.3", "48.0", "17.0")
    return data


def test_every_list_length_type_and_style_matches_intl(reference: Any) -> None:
    compared: set[str] = set()
    cases = 0
    for tag, kind, style, count, resolved, expected in reference["cases"]:
        if not _comparable(tag, resolved):
            continue
        got = format_list(reference["items"][:count], tag, type=kind, style=style)
        assert got == expected, (tag, kind, style, count)
        compared.add(tag)
        cases += 1
    assert (len(compared), cases) == (547, 25020)
    probes = {"en", "de", "ja", "zh-TW", "zh-HK", "sr-ME", "pa-PK", "iw", "tl", "de-AT-1996"}
    assert probes <= compared


def test_contextual_spanish_and_hebrew_words_match_intl(reference: Any) -> None:
    assert len(reference["contextual"]) > 1000
    for tag, kind, style, items, resolved, expected in reference["contextual"]:
        assert _comparable(tag, resolved), tag
        assert format_list(items, tag, type=kind, style=style) == expected, (tag, kind, items)


def test_hebrew_script_ranges_match_intl_for_every_code_point(reference: Any) -> None:
    assert [tuple(pair) for pair in reference["hebrew"]] == list(_HEBREW)


def test_unknown_tags_are_errors_here_and_fallbacks_in_intl(reference: Any) -> None:
    seen = {case[0] for case in reference["cases"] if case[0] in _SKIPPED_PROBES}
    assert seen == _SKIPPED_PROBES
    with pytest.raises(LookupError):
        resolve_locale("xx")
    assert resolve_locale("en_US") == "en"

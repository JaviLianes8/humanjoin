"""Seeded properties with hand-written independent reference algorithms."""

from __future__ import annotations

import random
import re
from collections.abc import Iterable

import pytest

from humanjoin import ListPattern, format_list, join, join_max, resolve_locale, supported_locales


def _join(items: Iterable[str], conj: str, oxford: bool) -> str:
    parts = list(items)
    if len(parts) < 2:
        return "".join(parts)
    separators = [", "] * (len(parts) - 1)
    separators[-1] = (", " if oxford and len(parts) > 2 else " ") + conj + " "
    return parts[0] + "".join(sep + item for sep, item in zip(separators, parts[1:], strict=True))


@pytest.mark.parametrize("seed", [181, 20261101, 729])
def test_seeded_join_and_truncation_properties(seed: int) -> None:
    rng = random.Random(seed)
    alphabet = " ab{}01\n\x00éא\U0001f600\ud800"
    for _ in range(2000):
        items = [
            "".join(rng.choices(alphabet, k=rng.randrange(15))) for _ in range(rng.randrange(20))
        ]
        conj, oxford = rng.choice(["and", "or", "", "&"]), rng.choice([True, False])
        assert join(iter(items), conj=conj, oxford=oxford) == _join(items, conj, oxford)
        limit = rng.randrange(22)
        kept = items if len(items) <= limit else [*items[:limit], f"{len(items) - limit} more"]
        assert join_max(iter(items), limit, conj=conj, oxford=oxford) == _join(kept, conj, oxford)
        assert format_list(iter(items), limit=limit) == _join(kept, "and", True)


def _substitute(pattern: str, previous: str, item: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return (previous, item)[int(match[1])]

    return re.sub(r"\{([01])\}", replace, pattern)


def _pattern(patterns: list[str], items: list[str]) -> str:
    if len(items) < 2:
        return "".join(items)
    result = items[0]
    for index, item in enumerate(items[1:], 1):
        slot = 0 if len(items) == 2 else 3 if index == len(items) - 1 else 1 if index == 1 else 2
        result = _substitute(patterns[slot], result, item)
    return result


@pytest.mark.parametrize("seed", [309, 20261101])
def test_seeded_custom_patterns_match_a_substitution_reference(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(3000):
        patterns = []
        for _ in range(4):
            left, right = rng.sample(["{0}", "{1}"], 2)
            patterns.append(
                rng.choice(["", "<", "("]) + left + " / " + right + rng.choice(["", ">", ")"])
            )
        items = rng.choices(["a", "{0}", "{1}", "", " ", "\udfff", "é"], k=rng.randrange(25))
        assert ListPattern(*patterns).format(iter(items)) == _pattern(patterns, items)


@pytest.mark.parametrize("seed", [471, 20261101])
def test_seeded_locale_lookup_has_bounded_typed_failures(seed: int) -> None:
    rng = random.Random(seed)
    known = set(supported_locales())
    for _ in range(5000):
        tag = "".join(rng.choices("en_-.@xA012é\x00\udfff", k=rng.randrange(300)))
        try:
            resolved = resolve_locale(tag)
        except (TypeError, ValueError, LookupError) as error:
            assert len(str(error)) < 100
        else:
            assert resolved in known
            assert resolve_locale(resolved) == resolved


def test_large_lists_and_reversed_wrappers_keep_every_item() -> None:
    size = 100000
    assert join(["x"] * size) == "x, " * (size - 1) + "and x"
    assert format_list(["x"] * size, "en") == join(["x"] * size)
    pattern = ListPattern("{1}{0}", "({1}{0})", "({1}{0})", "({1}{0})")
    assert pattern.format(["x"] * size) == "(x" * (size - 1) + "x" + ")" * (size - 1)


@pytest.mark.parametrize("seed", [917, 20261101])
def test_seeded_tail_templates_have_only_bounded_value_errors(seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(5000):
        template = "".join(rng.choices("{n}01:!sr.a[]_x\x00\ud800", k=rng.randrange(100)))
        try:
            result = join_max("abc", 1, more=template)
        except ValueError as error:
            assert len(str(error)) < 120 and error.__suppress_context__
        else:
            assert result == "a and " + template.format(n=2)


def test_items_are_stringified_once_even_when_hidden() -> None:
    calls: list[int] = []

    class Item:
        def __init__(self, value: int) -> None:
            self.value = value

        def __str__(self) -> str:
            calls.append(self.value)
            return str(self.value)

    assert join_max((Item(i) for i in range(4)), 1) == "0 and 3 more"
    assert calls == [0, 1, 2, 3]

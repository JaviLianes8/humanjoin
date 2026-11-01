"""Parse locale fields and apply the supported CLDR language aliases."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from ._options import locale_option

_SUBTAG = re.compile(r"[A-Za-z0-9]{1,8}")
_LANGUAGE = re.compile(r"[A-Za-z]{2,3}|[A-Za-z]{5,8}")
_MODIFIERS = {"latin": "Latn", "cyrillic": "Cyrl", "devanagari": "Deva"}


def _fields(subtags: list[str]) -> tuple[str, str, str, list[str]]:
    rest = subtags[1:]
    script = rest.pop(0).title() if rest and len(rest[0]) == 4 and rest[0].isalpha() else ""
    region = ""
    if rest and (
        (len(rest[0]) == 2 and rest[0].isalpha()) or (len(rest[0]) == 3 and rest[0].isdigit())
    ):
        region = rest.pop(0).upper()
    variants = []
    for part in rest:
        if len(part) == 1:
            break
        variants.append(part.lower())
    return subtags[0].lower(), script, region, variants


@lru_cache(maxsize=1024)
def _alias_order(key: str) -> tuple[int, tuple[bool, ...], tuple[str, ...]]:
    language, script, region, variants = _fields(key.split("-"))
    language = "" if language == "und" else language
    fields = (language, script, region)
    # CLDR counts field values, then prefers populated language/script/region/variant fields.
    count = sum(bool(field) for field in fields) + len(set(variants))
    return -count, tuple(not field for field in (*fields, variants)), (*fields, *sorted(variants))


def _alias(
    language: str, script: str, region: str, variants: list[str], aliases: dict[str, str]
) -> tuple[str, str, str, list[str]]:
    compounds = [key for key in aliases if "-" in key]
    while True:
        for key in sorted([*compounds, language], key=_alias_order):
            if key not in aliases:
                continue
            source, old_script, old_region, old_variants = _fields(key.split("-"))
            if source not in (language, "und"):
                continue
            if (old_script and old_script != script) or (old_region and old_region != region):
                continue
            if not set(old_variants) <= set(variants):
                continue
            target, new_script, new_region, new_variants = _fields(aliases[key].split("-"))
            language = target if target != "und" else language
            script = new_script if old_script else script or new_script
            region = new_region if old_region else region or new_region
            variants = [part for part in variants if part not in old_variants] + new_variants
            break  # A language replacement can expose a more specific compound rule.
        else:
            return language, script, region, variants


def parse(locale: str, data: dict[str, Any]) -> tuple[str, str, str, list[str]]:
    locale = locale_option(locale)
    tag, _, modifier = locale.partition("@")
    subtags = tag.split(".", 1)[0].replace("_", "-").split("-")
    if subtags[0].lower() == "root":
        subtags[0] = "und"
    if not all(_SUBTAG.fullmatch(part) for part in subtags) or not _LANGUAGE.fullmatch(subtags[0]):
        raise ValueError("not a locale tag")
    if len(subtags) > 1 and len(subtags[1]) == 3 and subtags[1].isalpha():
        raise ValueError("extended language subtags are not supported")
    language, script, region, variants = _fields(subtags)
    script = script or _MODIFIERS.get(modifier.lower(), "")
    region = data["regions"].get(region, region)
    return _alias(language, script, region, variants, data["aliases"])

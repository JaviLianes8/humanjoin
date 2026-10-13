"""Derive the package pattern table, src/humanjoin/_cldr.json, from the CLDR JSON packages.

The CLDR packages are fetched into tests/upstream by scripts/fetch_upstream.py and are not
part of the repository. The table keeps only facts: the list patterns of every locale, the
parent locales, the likely script of a language and region where a language has several,
and the language codes CLDR replaces.

    python scripts/build_patterns.py
"""

from __future__ import annotations

import json
import re
import sys
import tarfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT / "tests" / "upstream"
TARGET = ROOT / "src" / "humanjoin" / "_cldr.json"
VERSION = "48.0.0"

# CLDR key suffix for each (type, style) pair, in the order the table stores them.
KINDS = [
    (kind, style) for kind in ("standard", "or", "unit") for style in ("", "-short", "-narrow")
]
LANGUAGE = re.compile(r"[a-z]{2,3}")
REGION = re.compile(r"[A-Z]{2}|\d{3}")
TAG = re.compile(r"[a-z]{2,3}(-[A-Z][a-z]{3})?(-([A-Z]{2}|\d{3}))?")


def _members(path: Path) -> dict[str, Any]:
    """Every JSON member of a CLDR npm tarball, keyed by its path inside ``package/``."""
    found: dict[str, Any] = {}
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            if member.isfile() and member.name.endswith(".json"):
                handle = archive.extractfile(member)
                assert handle is not None
                found[member.name.removeprefix("package/")] = json.load(handle)
    return found


def derive(upstream: Path = UPSTREAM) -> dict[str, Any]:
    """The pattern table as a JSON-ready dict, derived from the two CLDR tarballs."""
    misc = _members(upstream / f"cldr-misc-full-{VERSION}.tgz")
    core = _members(upstream / f"cldr-core-{VERSION}.tgz")
    pool: dict[tuple[str, str, str, str], int] = {}
    locales: dict[str, list[int]] = {}
    for name, body in sorted(misc.items()):
        if not name.endswith("/listPatterns.json"):
            continue
        locale = name.split("/")[1]
        sets = body["main"][locale]["listPatterns"]
        row = []
        for kind, style in KINDS:
            data = sets[f"listPattern-type-{kind}{style}"]
            quad = (data["2"], data["start"], data["middle"], data["end"])
            row.append(pool.setdefault(quad, len(pool)))
        locales[locale] = row
    supplemental = core["supplemental/parentLocales.json"]["supplemental"]["parentLocales"]
    parents = dict(sorted(supplemental["parentLocale"].items()))
    likely = core["supplemental/likelySubtags.json"]["supplemental"]["likelySubtags"]
    aliases = core["supplemental/aliases.json"]["supplemental"]["metadata"]["alias"]
    return {
        "cldr": VERSION,
        "patterns": [list(quad) for quad in pool],
        "locales": locales,
        "parents": parents,
        "scripts": _likely_scripts(locales, likely),
        "aliases": _language_aliases(locales, aliases["languageAlias"]),
        "regions": _region_aliases(aliases["territoryAlias"]),
    }


def _likely_scripts(locales: dict[str, list[int]], likely: dict[str, str]) -> dict[str, str]:
    """The likely script of each language written in several, and of its regions that differ.

    Only languages with locales in more than one script need it: that is what makes
    ``zh-TW`` read the Traditional Chinese patterns and ``zh-SG`` reach ``zh-Hans-SG``.
    """
    multi = {name.split("-")[0] for name in locales if _script(name)}
    found: dict[str, str] = {}
    for key, value in sorted(likely.items()):
        parts = key.split("-")
        if parts[0] not in multi or not 1 <= len(parts) <= 2:
            continue
        if len(parts) == 2 and not REGION.fullmatch(parts[1]):
            continue
        default = likely.get(parts[0], "").split("-")
        script = value.split("-")[1]
        if len(parts) == 1 or (len(default) > 1 and script != default[1]):
            found[key] = script
    return found


def _script(name: str) -> bool:
    parts = name.split("-")
    return len(parts) > 1 and len(parts[1]) == 4


def _language_aliases(locales: dict[str, list[int]], table: dict[str, Any]) -> dict[str, str]:
    """Language codes CLDR replaces, mapped to a replacement whose language has data.

    A replacement may carry a script or region (``sh`` is ``sr-Latn``, ``cnr`` is ``sr-ME``).
    """
    languages = {name.split("-")[0] for name in locales}
    found: dict[str, str] = {}
    for key, entry in sorted(table.items()):
        target = entry["_replacement"]
        if LANGUAGE.fullmatch(key) and TAG.fullmatch(target) and target.split("-")[0] in languages:
            found[key] = target
    return found


def _region_aliases(table: dict[str, Any]) -> dict[str, str]:
    """Region codes CLDR replaces by exactly one other region (``UK`` is ``GB``)."""
    return {
        key: entry["_replacement"]
        for key, entry in sorted(table.items())
        if REGION.fullmatch(key) and REGION.fullmatch(entry["_replacement"])
    }


def render(table: dict[str, Any]) -> str:
    return json.dumps(table, ensure_ascii=True, separators=(",", ":"), sort_keys=True) + "\n"


def main() -> int:
    TARGET.write_text(render(derive()), encoding="ascii", newline="\n")
    print(f"wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

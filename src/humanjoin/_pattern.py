"""List patterns and the formatting algorithm of the ICU list formatter."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

__all__ = ["ListPattern"]

# Code points whose Unicode script is Hebrew, from Scripts.txt of Unicode 17.0.0
# (https://www.unicode.org/Public/17.0.0/ucd/Scripts.txt), adjacent ranges merged.
_HEBREW = (
    (0x0591, 0x05C7),
    (0x05D0, 0x05EA),
    (0x05EF, 0x05F4),
    (0xFB1D, 0xFB36),
    (0xFB38, 0xFB3C),
    (0xFB3E, 0xFB3E),
    (0xFB40, 0xFB41),
    (0xFB43, 0xFB44),
    (0xFB46, 0xFB4F),
)

# The ICU list formatter rewrites these exact patterns depending on the last item.
_SPANISH_AND = "{0} y {1}"
_SPANISH_OR = "{0} o {1}"
_VAV = chr(0x05D5)  # HEBREW LETTER VAV, the word "and"
_HEBREW_AND = "{0} " + _VAV + "{1}"


def _is_hebrew(char: str) -> bool:
    point = ord(char)
    return any(low <= point <= high for low, high in _HEBREW)


def _to_e(text: str) -> bool:
    """Spanish "y" becomes "e" before "i" and "hi", but not before "hia" or "hie"."""
    if text[:1] in ("i", "I"):
        return True
    return (
        text[:1] in ("h", "H") and text[1:2] in ("i", "I") and text[2:3] not in ("a", "A", "e", "E")
    )


def _to_u(text: str) -> bool:
    """Spanish "o" becomes "u" before "o", "ho" and "8", and before the number 11."""
    if text[:1] in ("o", "O", "8") or (text[:1] in ("h", "H") and text[1:2] in ("o", "O")):
        return True
    return text[:2] == "11" and text[2:3] in ("", " ")


def _contextual(pattern: str, last: str, language: str | None) -> str:
    if not last:
        return pattern
    if language == "es":
        if pattern == _SPANISH_AND and _to_e(last):
            return "{0} e {1}"
        if pattern == _SPANISH_OR and _to_u(last):
            return "{0} u {1}"
    elif language in ("he", "iw") and pattern == _HEBREW_AND and not _is_hebrew(last[0]):
        return "{0} " + _VAV + "-{1}"
    return pattern


def _check(name: str, pattern: object) -> None:
    if not isinstance(pattern, str):
        raise TypeError(f"{name} must be a str, not {type(pattern).__name__}")
    for slot in ("{0}", "{1}"):
        if pattern.count(slot) != 1:
            raise ValueError(f"{name} must contain {slot} exactly once: {pattern!r}")


def _fill(pattern: str, joined: str, item: str) -> str:
    # Slicing the pattern, not replacing in the result, keeps braces inside items intact.
    first, second = pattern.index("{0}"), pattern.index("{1}")
    if first < second:
        return pattern[:first] + joined + pattern[first + 3 : second] + item + pattern[second + 3 :]
    return pattern[:second] + item + pattern[second + 3 : first] + joined + pattern[first + 3 :]


@dataclass(frozen=True)
class ListPattern:
    """The four patterns that format a list, as CLDR defines them.

    ``two`` joins a list of exactly two items. A longer list starts with its first item,
    then ``start`` adds the second, ``middle`` each following one but the last, and ``end``
    the last; in each pattern ``{0}`` is the text so far and ``{1}`` the new item.
    ``language`` selects the contextual rules the ICU formatter applies on top of the
    patterns: ``es`` (``y`` to ``e``, ``o`` to ``u``) and ``he`` (a hyphen after the letter vav
    before a word in another script); any other value applies none.
    """

    two: str
    start: str
    middle: str
    end: str
    language: str | None = None

    def __post_init__(self) -> None:
        for name in ("two", "start", "middle", "end"):
            _check(name, getattr(self, name))
        if self.language is not None and not isinstance(self.language, str):
            raise TypeError(f"language must be a str or None, not {type(self.language).__name__}")

    def format(self, items: Iterable[object]) -> str:
        """Join ``items``, each converted with ``str``, into one phrase."""
        parts = [str(item) for item in items]
        if not parts:
            return ""
        if len(parts) == 1:
            return parts[0]
        last = parts[-1]
        if len(parts) == 2:
            return _fill(_contextual(self.two, last, self.language), parts[0], last)
        text = _fill(self.start, parts[0], parts[1])
        for item in parts[2:-1]:
            text = _fill(self.middle, text, item)
        return _fill(_contextual(self.end, last, self.language), text, last)

"""Normalize primitive options before invoking validation or cache operations."""

from __future__ import annotations

from typing import cast


def text_option(value: object, name: str) -> str:
    if not issubclass(type(value), str):
        raise TypeError(f"{name} must be a str")
    return str.__str__(cast(str, value))


def locale_option(value: object) -> str:
    locale = text_option(value, "locale")
    if len(locale) > 255:
        raise ValueError("locale must contain at most 255 characters")
    return locale

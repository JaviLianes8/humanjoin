"""Join a list of strings into a natural-language phrase, with Oxford comma and overflow limit."""

from __future__ import annotations

from ._join import join, join_max

__version__ = "0.1.0"

__all__ = ["join", "join_max"]

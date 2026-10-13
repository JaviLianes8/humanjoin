"""Command line: ``humanjoin a b c --locale de`` prints ``a, b und c``."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TextIO, cast

from ._format import ListStyle, ListType, format_list
from ._locale import cldr_version, supported_locales

__all__ = ["main"]


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="humanjoin",
        description="Join items into one phrase the way a language writes a list (Unicode CLDR).",
        epilog="Without ITEM arguments the items are read from stdin, one per non-blank line.",
    )
    parser.add_argument("items", nargs="*", metavar="ITEM", help="the items, in order")
    parser.add_argument("-l", "--locale", default="en", help="BCP 47 locale (default: en)")
    parser.add_argument(
        "-t",
        "--type",
        default="conjunction",
        choices=["conjunction", "disjunction", "unit"],
        help="list type (default: conjunction)",
    )
    parser.add_argument(
        "-s",
        "--style",
        default="long",
        choices=["long", "short", "narrow"],
        help="list style (default: long)",
    )
    parser.add_argument("--limit", type=int, help="show at most this many items")
    parser.add_argument(
        "--more", default="{n} more", help="tail for hidden items, {n} is the count"
    )
    parser.add_argument(
        "--locales", action="store_true", help="list the supported locales and exit"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"humanjoin {__version__} (CLDR {cldr_version()})",
    )
    return parser


def _utf8(stream: TextIO) -> None:
    # Pipes default to the legacy code page on Windows, which cannot carry most scripts.
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None and not stream.isatty():
        reconfigure(encoding="utf-8")


def main(
    argv: Sequence[str] | None = None, stdin: TextIO | None = None, stdout: TextIO | None = None
) -> int:
    """Run the command line; returns the exit status (0 ok, 2 bad arguments or locale)."""
    if stdin is None:
        stdin = sys.stdin
        _utf8(stdin)
    if stdout is None:
        stdout = sys.stdout
        _utf8(stdout)
    parser = _parser()
    args = parser.parse_args(argv)
    if args.locales:
        stdout.write("\n".join(supported_locales()) + "\n")
        return 0
    items = args.items or [line.strip("\r\n") for line in stdin if line.strip()]
    try:
        text = format_list(
            items,
            args.locale,
            type=cast(ListType, args.type),
            style=cast(ListStyle, args.style),
            limit=args.limit,
            more=args.more,
        )
    except (LookupError, ValueError) as error:
        parser.exit(2, f"humanjoin: error: {error}\n")
    stdout.write(text + "\n")
    return 0

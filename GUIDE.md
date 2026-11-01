# humanjoin guide

The public API is imported from `humanjoin`. The ten names in `__all__`, their
parameter names, defaults and built-in error families are stable for 1.x. The
package also exposes `__version__`. Python 3.10 or later is required.

## English lists and overflow

`join` converts each item using `str`, consumes a finite iterable once, and keeps
order, empty strings, whitespace and braces. A string input is an iterable of
characters. Zero items produce `""`; one is returned alone; two use the conjunction
without a comma. Longer lists use commas and, by default, an Oxford comma.
`conj` is any string, including empty text, and `oxford` must be a `bool`.

`join_max` accepts a nonnegative integer `limit` (not `bool`). `format_list`
also allows `limit=None` for no truncation. The entire input is consumed and
converted, including hidden items. Neither function accepts infinite iterables.
When items are hidden, keep the first `limit` and append one tail item; zero keeps
only the tail. If nothing is hidden, no tail template is parsed or callback called.

`more` is a string or a callable accepting the hidden count and returning an object
converted with `str`. Templates may contain literal text, escaped braces, and only
the exact field `{n}`. Python integer formatting and `!s`, `!r`, `!a` conversions
are supported, with width and precision at most 10000. Attribute/index access and
nested fields are rejected. The default tail is English; supply a localized one.

```python
from humanjoin import join, join_max, format_list

print(join(["tea", "coffee", "water"], conj="or", oxford=False))
print(join_max(range(5), 0))
print(join_max("abcd", 1, more="{{remaining}} {n:02d}"))
print(format_list("abcd", "de", limit=2, more=lambda n: f"{n} weitere"))
# tea, coffee or water
# 5 more
# a and {remaining} 03
# a, b und 2 weitere
```

## Locales and list patterns

`ListType` is `Literal["conjunction", "disjunction", "unit"]`; `ListStyle` is
`Literal["long", "short", "narrow"]`. `format_list` and `list_pattern` default to
English, conjunction, long. `supported_locales()` returns a sorted immutable tuple
of 766 tags, and `cldr_version()` returns `"48.0.0"`.

Locale lookup accepts case-insensitive BCP 47 style tags and POSIX spellings such
as `sr_RS.UTF-8@latin`. Encoding suffixes do not select patterns. The script
modifiers `latin`, `cyrillic` and `devanagari` do; other modifiers are ignored.
Deprecated language/region codes, likely scripts and CLDR parent locales are
applied. Extensions and private-use subtags do not select patterns. This is a
locale lookup utility, not a full BCP 47 validator: variant and extension grammar
is not exhaustively checked. Extended language subtags are unsupported.

All tags returned by `supported_locales` resolve to themselves. A tag with its
own CLDR entry stays that tag even if its patterns equal a parent's. Unknown
languages raise `LookupError`; explicit `und` and `root` select CLDR root patterns.
A known CLDR parent may itself select root. Input tags are limited to 255 characters.

```python
from humanjoin import resolve_locale, list_pattern, ListPattern

print(resolve_locale("sr_RS@latin"))
print(resolve_locale("en-IN"))
print(list_pattern("en", "disjunction").format(["tea", "coffee"]))
custom = ListPattern("({1}/{0})", "<{0}+{1}>", "[{1}|{0}]", "{0}={1}")
print(custom.format("abcd"))
# sr-Latn
# en-IN
# tea or coffee
# [c|<a+b>]=d
```

`ListPattern` is a frozen, hashable dataclass with `two`, `start`, `middle`, `end`
and optional `language`. Every pattern must contain `{0}` and `{1}` exactly once;
other braces are literal. Zero/one items need no pattern; two use `two`; longer
lists apply `start`, then `middle` for each intermediate item, then `end`.
Placeholders can be reversed, with arbitrary prefixes and suffixes. Item text is
never interpreted as a template. Formatting takes linear time in input and output
size and memory proportional to input and output size.

The optional language selects ICU's contextual rules for exact Spanish `y`/`o`
and Hebrew vav patterns. Spanish `y` becomes `e` before `i` or `hi` except `hia`
and `hie`; `o` becomes `u` before `o`, `ho`, `8`, or `11` followed by space or end.
These checks are ASCII case-insensitive, not general phonetic analysis. Hebrew
`he` and `iw` insert a hyphen before a non-Hebrew-script first character. Empty
last items do not trigger a change. Other languages use the patterns literally.

## Errors

| Condition | Error |
| --- | --- |
| Wrong locale/type/style, pattern/language, conjunction, Oxford flag, limit or tail type | `TypeError` |
| Negative limit; unsupported type/style; malformed, overlong or extlang locale; missing/duplicate placeholders | `ValueError` |
| Invalid or excessive tail template, when truncation is needed | `ValueError` |
| No locale data after lookup | `LookupError` |

Validation messages are bounded and omit supplied values. Invalid options are
checked before consuming items, except template syntax, which is checked only
when a tail is required. Exceptions raised by user iterators, item `__str__`
methods or tail callbacks propagate unchanged; their messages are the caller's
responsibility. This includes passing a non-iterable as `items`. Filesystem and
stream errors also propagate. Exact message wording is not a compatibility promise.

## Command line

`humanjoin` and `python -m humanjoin` accept ITEM arguments and `--locale`/`-l`,
`--type`/`-t`, `--style`/`-s`, `--limit`, `--more`, `--locales`, `--version`, `--help`.
Defaults match `format_list`. Arguments preserve spaces; with no items, stdin is
read as UTF-8, one item per line. The first byte order mark, surrounding whitespace
and blank lines are removed. Pipes use UTF-8 output. A terminal without items is
an error. Empty piped input prints a newline. `--locales` prints one tag per line.
Success exits 0; usage, locale, template and malformed UTF-8 errors exit 2 on stderr.
Argument errors do not echo supplied values. Use `--` before items beginning with `-`.

## Upgrading from 0.2.0

All public names, signatures, list data and valid formatting results remain.
The [CHANGELOG](https://github.com/JaviLianes8/humanjoin/blob/main/CHANGELOG.md)
lists the tightened validation: boolean Oxford flag, tail type validation even
without truncation, bounded locale length and constrained overflow templates.
Bad options are now validated before iteration, and messages no longer include
supplied values. Long custom lists format in linear time. Pickled patterns work
in both directions across the upgrade; new pickles refer to `humanjoin.ListPattern`.

## Reference data

The table is derived from CLDR 48, with ICU 78.3 contextual rules and Unicode 17
Hebrew script ranges. These versions are pinned rather than following the host's
locale data. The [manifest](https://github.com/JaviLianes8/humanjoin/blob/main/tests/upstream/MANIFEST.json)
records source URLs, revisions, licenses and hashes. Run `scripts/fetch_upstream.py`
to fetch the reference sources and generate Node 24.18 `Intl.ListFormat` output.
Set `HUMANJOIN_UPSTREAM` to choose the local reference folder. Reference tests skip
cleanly when these optional files are absent; fetched source files are not shipped.

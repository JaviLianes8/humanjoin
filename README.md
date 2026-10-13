# humanjoin

Join a list into a natural-language phrase: "a, b, and c" with or without the Oxford comma,
"a, b, and 3 more" when the list is long, and the list patterns of every Unicode CLDR locale
for "a, b und c", "a、b和c" or "a, b o c". Typed, zero dependencies.

## Install

```
pip install humanjoin
```

## Usage

English with a chosen conjunction, as in `0.1`:

```python
from humanjoin import join, join_max

print(join(["apple", "pear", "plum"]))
print(join(["apple", "pear", "plum"], oxford=False))
print(join(["red", "green"], conj="or"))
print(join_max(["a", "b", "c", "d", "e"], 2))
print(join_max(["a", "b", "c", "d", "e"], 2, conj="or", oxford=False))
# apple, pear, and plum
# apple, pear and plum
# red or green
# a, b, and 3 more
# a, b or 3 more
```

Any language, with the vocabulary of `Intl.ListFormat`: `type` is `conjunction`,
`disjunction` or `unit`, `style` is `long`, `short` or `narrow`.

```python
from humanjoin import format_list

items = ["Ana", "Ben", "Cleo"]
print(format_list(items, "de"))
print(format_list(items, "en-GB"))
print(format_list(items, "fr", type="disjunction"))
print(format_list(items, "zh-TW"))
print(format_list(["5 ft", "2 in"], "en", type="unit", style="narrow"))
print(format_list(items, "en", style="short"))
# Ana, Ben und Cleo
# Ana, Ben and Cleo
# Ana, Ben ou Cleo
# Ana、Ben和Cleo
# 5 ft 2 in
# Ana, Ben, & Cleo
```

The rules ICU applies on top of the data are applied too: Spanish "y" becomes "e" before an
"i" sound and "o" becomes "u" before an "o" sound.

```python
from humanjoin import format_list

print(format_list(["padre", "hijo"], "es"))
print(format_list(["siete", "ocho"], "es", type="disjunction"))
# padre e hijo
# siete u ocho
```

Long lists fold into a tail. `more` is a template with `{n}` or a callable taking the hidden
count, so plurals and other languages are up to you:

```python
from humanjoin import format_list

names = ["Ana", "Ben", "Cleo", "Dan"]
print(format_list(names, "en", limit=2))
print(format_list(names, "de", limit=3, more="{n} weitere"))
print(format_list(names, "en", limit=3, more=lambda n: f"{n} other" + "s" * (n != 1)))
# Ana, Ben, and 2 more
# Ana, Ben, Cleo und 1 weitere
# Ana, Ben, Cleo, and 1 other
```

Locales and patterns:

```python
from humanjoin import list_pattern, resolve_locale

print(resolve_locale("pt_BR.UTF-8"), resolve_locale("zh-TW"), resolve_locale("iw"))
pattern = list_pattern("en", "disjunction")
print(pattern.end)
print(pattern.format(["tea", "coffee", "water"]))
# pt zh-Hant he
# {0}, or {1}
# tea, coffee, or water
```

From the shell, items as arguments or one per line on stdin:

```
$ humanjoin tea coffee water --locale it
tea, coffee e water
$ printf 'tea\ncoffee\n' | humanjoin -l ja -t disjunction
teaまたはcoffee
```

## API

| Name | What it does |
| --- | --- |
| `join(items, *, conj="and", oxford=True)` | English-style phrase with any conjunction and an Oxford comma toggle. |
| `join_max(items, limit, *, more="{n} more", conj="and", oxford=True)` | `join`, keeping at most `limit` items and folding the rest into a tail. |
| `format_list(items, locale="en", *, type=, style=, limit=None, more=)` | The phrase `locale` writes, from the CLDR list patterns. |
| `list_pattern(locale="en", type="conjunction", style="long")` | The `ListPattern` behind `format_list`. |
| `ListPattern(two, start, middle, end, language=None)` | Four validated patterns and the `format` algorithm; build your own. |
| `resolve_locale(locale)` | The CLDR locale whose data a tag uses. |
| `supported_locales()` | Every CLDR locale in the table, sorted. |
| `cldr_version()` | The CLDR release the table comes from. |
| `ListType`, `ListStyle` | `Literal` types of the `type` and `style` values. |

Items are converted with `str`. A wrong `type` or `style`, a negative `limit` or a malformed
locale tag raise `ValueError`; a language CLDR has no data for raises `LookupError`.

## How it compares with `Intl.ListFormat`

The table holds the list patterns of all 766 locales of CLDR 48, and the formatter follows
the ICU list formatter. The test suite checks every locale, type and style against the CLDR
files and against `Intl.ListFormat` of Node 24 (ICU 78.3, CLDR 48) for lists of zero to four
items. The differences are deliberate:

- ICU ships fewer locales than CLDR and falls back to the default locale of the machine
  when it has none; here every CLDR locale has its own data and an unknown language raises.
- `und` and `root` name the CLDR root locale instead of the default locale.
- POSIX spellings such as `pt_BR.UTF-8` are accepted.
- Items do not have to be strings.

Locale resolution replaces deprecated codes (`iw` is `he`), adds the likely script where a
language is written in several (`zh-TW` reads `zh-Hant`, `sr-ME` reads `sr-Latn-ME`), then
follows the CLDR parent locales (`en-IN` and `en-AU` read `en-001`, `pt-AO` reads `pt-PT`)
and drops subtags until it finds data.

## Why

Joining a list into readable prose is written again in every project, and the details are
easy to get wrong: no comma for two items, the Oxford comma toggle, an "and N more" tail,
and every other language. `humanize.natural_list` has no Oxford comma and no overflow limit.
`inflect.join` has the Oxford comma but pulls in dependencies and is English only. Babel has
`format_list` with CLDR data, but it is a large dependency and has no truncation. This is a
small typed primitive for exactly those cases.

## Development

```
python scripts/fetch_upstream.py   # CLDR, ICU, Unicode and ECMA-402 reference files, not committed
python scripts/build_patterns.py   # derive src/humanjoin/_cldr.json from the CLDR files
pwsh scripts/check.ps1             # format, lint, types, tests
```

## License

MIT, see [LICENSE](LICENSE). The pattern table is derived from Unicode CLDR data, used under
the Unicode License v3, see [LICENSE-UNICODE](LICENSE-UNICODE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/

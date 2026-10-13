# humanjoin improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: CLDR 48 list patterns, ICU 78.3 list formatter, Unicode 17 scripts, Intl.ListFormat output
- [x] Locale pattern table derived from CLDR, with the Unicode licence shipped
- [x] `format_list`, `list_pattern`, `ListPattern`, locale resolution, contextual Spanish and Hebrew rules
- [x] `join` and `join_max` fixes: validated arguments, `join_max` honours `conj` and `oxford`, callable tail
- [x] Command line
- [x] Contracts: CLDR table, Intl.ListFormat output, README examples, installed wheel
- [x] Docs and packaging: README, CHANGELOG, metadata, sdist contents
- [x] Gates: ruff format, ruff check, mypy --strict, pytest
- [ ] Mutation run: removing guarded logic makes the suite fail
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` gives `join(items, conj=, oxford=)` and `join_max(items, limit, more=)`. Probed:

- English only. The conjunction is a bare word, so no other language can be expressed:
  German has no serial comma, Chinese joins with `、` and `和` without spaces, Japanese with
  `、`, Maori puts "or" after the last item (`a, b, c rānei`), Spanish switches `y` to `e`
  before an "i" sound and `o` to `u` before an "o" sound, Hebrew attaches the conjunction to
  the next word.
- No disjunction or unit lists, no short or narrow widths, no locale lookup at all.
- `join_max` ignores the options of `join`: it always uses "and" with the Oxford comma, so
  `join_max(items, 2)` cannot produce "a, b or 3 more".
- `join_max` with a negative limit silently folds every item into the tail, and a `bool`
  passes as a limit. The `more` template can only pluralise through the template text.

## Ranked improvements

1. **CLDR list patterns as the source of truth.** Every locale of CLDR 48 (766 of them) with
   the nine pattern sets (`standard`, `or`, `unit`, each `long`, `short`, `narrow`), each set
   being the four patterns `2`, `start`, `middle`, `end`. The table is derived by a script
   from the CLDR JSON packages and shipped as a compact package data file; the CLDR files
   themselves stay in an ignored local folder. The Unicode licence ships with the wheel.
2. **`format_list(items, locale, type=, style=)`** with the vocabulary of
   `Intl.ListFormat`: `type` is `conjunction`, `disjunction` or `unit`, `style` is `long`,
   `short` or `narrow`. Formatting follows the ICU list formatter: the first item, then the
   start, middle and end patterns applied left to right, so patterns with text after `{1}`
   work. Output is checked against `Intl.ListFormat` of Node 24.18 (ICU 78.3, CLDR 48).
3. **Locale resolution like ICU.** BCP 47 or POSIX spelling, case folded, deprecated
   language codes replaced (`iw` to `he`, `tl` to `fil`), the CLDR parent locales
   (`en-IN` to `en-001`, `pt-AO` to `pt-PT`), and a likely script inserted where a language
   has several (`zh-TW` reads Traditional Chinese, `sr-ME` Latin Serbian). An unknown
   language raises `LookupError` instead of silently using English. `resolve_locale` says
   which CLDR locale was used.
4. **Contextual rules ICU applies on top of the data.** Spanish `y` becomes `e` before
   "i" and "hi" (not "hia", "hie"), `o` becomes `u` before "o", "ho", "8" and "11";
   Hebrew `ו` takes a hyphen before a word not in Hebrew script. Script ranges are derived
   from the Unicode 17 `Scripts.txt`.
5. **`ListPattern`** frozen, validated value type with `format`, so callers can build their
   own pattern (or start from `list_pattern(locale, ...)`) and keep the same algorithm.
6. **Truncation everywhere.** `format_list(..., limit=, more=)` and `join_max` share one
   rule; `more` accepts a template or a callable taking the count, for real plurals.
   `join_max` honours `conj` and `oxford`. Negative or non-integer limits raise.
7. **Typed API.** `ListType` and `ListStyle` literal aliases, `mypy --strict` clean,
   unknown `type`, `style` or locale values rejected at run time with clear messages.
8. **Command line.** `humanjoin a b c --locale de --type disjunction`, items from
   arguments or stdin lines, `--limit` and `--more`, `--locales` to list the table. It fits:
   shell scripts that build a message from a list want exactly this.
9. **Contracts.** Pattern table equals a fresh derivation from CLDR; every locale, type
   and style matches `Intl.ListFormat` for one to four items; contextual words match too;
   README examples run; the installed wheel and its console script are driven from an
   empty folder.
10. **Docs and packaging.** README with executed examples and an API table, CHANGELOG,
    keywords, classifiers, licence expression, an sdist without planning notes or fetched
    files.

## Out of scope

- Inflecting the items themselves (case, gender); CLDR list patterns do not cover it.
- Locale negotiation against the user environment: the caller passes the locale.
- `formatToParts`: spans are not exposed in this round.

# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The ten public names, function signatures and defaults of 0.2.0 remain supported.
  CLDR 48.0.0 supplies 766 locales and all nine list type/style combinations. Custom
  patterns, contextual Spanish and Hebrew rules, truncation and both CLI entry points
  are stable. Python 3.10 and later are supported without runtime dependencies.

### Changed

- Library validation errors and CLI argument errors no longer echo supplied values or
  type names. Built-in `TypeError`, `ValueError` and `LookupError` remain the error families.
- `oxford` must be a `bool`; other values now raise `TypeError` rather than using truthiness.
- `more` must be text or callable even when no items are hidden. Limit and tail type
  validation, and `join_max` conjunction/Oxford validation, now happen before consuming
  items. Invalid options no longer consume them (template syntax is checked on overflow).
- Overflow templates allow only the exact field `n`, optional `!s`, `!r` or `!a`, and
  integer format specifications with width and precision at most 10000. Nested fields,
  attribute/index access and excessive padding now raise `ValueError`. Invalid template
  syntax still matters only when items are hidden; errors suppress the original exception.
- Locale inputs longer than 255 characters now raise `ValueError` before parsing or caching.
- `ListPattern` identifies its public module as `humanjoin`. Old pickles still load;
  new pickles can also be read by 0.2.0 through its existing public re-export.
- The accidental `annotations` attribute is removed from the package namespace; it
  was never part of `__all__`.

### Fixed

- Oxford flag validation requires an actual boolean, so spoofed or raising
  `__class__` properties cannot bypass validation or replace `TypeError`.
- Overflow tails are classified by actual string ancestry. Callable tails with
  overridden `__class__` properties work in both truncating functions, while
  invalid tails raise `TypeError` before item iteration without reading the property.
- Multi-target territory aliases select the likely territory for the canonical
  language and script when available among the replacements, otherwise the first
  replacement. For example, `en-200` selects `en-CZ` and `kk-SU` selects `kk-KZ`.
- Language aliases are retained even when the replacement has no bundled patterns.
  Deprecated spellings such as `zh-hakka`, `zh-xiang` and `hy-arevmda` now raise
  `LookupError`, matching their canonical spellings `hak`, `hsn` and `hyw`.
- Text option validation checks actual string ancestry, so a non-string value's
  overridden `__class__` property cannot run or replace the documented `TypeError`.
  This covers locales, list types/styles, conjunctions and custom pattern fields.
- CLDR aliases follow field-based precedence and repeat until canonical, so
  `nor-nynorsk`, `nor-bokmal` and `aar-saaho` select `nn`, `nb` and `ssy`.
- Multi-variant locale fallback searches available combinations before the base,
  including after default-script removal: `be-tarask-fonipa` selects `be-tarask`
  and `ca-Latn-ES-fonipa-valencia` selects `ca-ES-valencia`.
- Unavailable variants no longer suppress likely-script regional fallback:
  `zh-SG-fonipa` and `zh-SG-1996` select `zh-Hans-SG`. Variant data is retained
  during script insertion, and explicit regional parents remain authoritative.
- Integer limit validation inspects the actual type before normalization, so an
  overridden `__class__` property cannot run or replace the documented errors.
- Unicode decimal digits, including mixed alphabets and leading zeros, obey the 10000
  overflow-template width and precision limits in both public functions and the CLI.
- Compound CLDR language aliases such as `no-nynorsk` resolve before fallback. Explicit
  scripts and regions are retained, and removing a default script preserves variant locales
  such as `ca-Latn-ES-valencia` (`ca-ES-valencia`).
- Locales with an unsupported nonlikely script, such as `ru-Latn` and `en-Cyrl`, inherit
  CLDR root patterns instead of the language's usual script. Unknown languages still fail.
- String and integer option subclasses are normalized to their underlying built-in values
  before validation, hashing or formatting. Overridden methods can no longer bypass bounds
  or inject errors. This includes custom pattern fields; item and callback coercion is unchanged.
- Invalid CLI locale and limit options fail before reading stdin, including an open pipe.
  Template syntax is still checked only when items overflow the limit.
- Long custom and locale lists are assembled in linear time in the input and output size,
  including patterns with reversed placeholders, prefixes or suffixes. Results are unchanged.

### Added

- Contracts require `supported_locales()` to return an immutable tuple and prevent
  extension or private-use payloads from selecting available locale variants.
  These checks preserve existing behavior.
- Contracts preserve adjacent high/low surrogate code points as distinct from
  their corresponding supplementary Unicode character in conjunctions, overflow
  templates, all custom pattern fields and stored custom language values,
  including string subclasses. These contracts preserve existing behavior.
- Contracts preserve lone high and low surrogates in conjunctions, overflow
  templates, all custom pattern fields and stored custom language values,
  including string subclasses. These contracts preserve existing behavior.
- Contracts preserve embedded NULs and leading BOMs in text options, retain
  region/script-suffixed custom language strings without contextual rewriting,
  and distinguish empty custom language strings from `None`. Uppercase and
  mixed-case type/style selectors raise `ValueError` before item iteration.
  These contracts include string subclasses and preserve existing behavior.
- Contracts preserve exact CRLF and decomposed Unicode text in conjunctions,
  overflow templates and custom pattern fields, including string subclasses.
  Custom language codes retain their case and select contextual rules only by
  exact match. Padded locale, type and style selectors raise `ValueError` before
  item iteration. These contracts preserve existing behavior.
- Exact-output contracts preserve conjunction and custom-pattern whitespace and
  literal language values, including normalized string subclasses.
- Contracts reject noninteger limits with raising `__class__` properties through
  both truncating functions without invoking the property or consuming items.
- Exact-byte contracts preserve noninitial stdin BOM characters through both CLI
  entry points while removing an initial BOM. Locale contracts require the correct
  source language for compound aliases and preserve unrelated variants through aliasing.
- Exact-byte subprocess contracts preserve whitespace in ITEM arguments through both CLI
  entry points. Callable-tail contracts retain eager `str` conversion followed by item
  coercion, including a callback result whose `__str__` returns a string subclass at limit zero.
- Executable public docstrings, a detailed guide, seeded property tests, installed-wheel
  and PyPI upgrade checks, and package metadata declaring production stability.
- `HUMANJOIN_UPSTREAM` selects a separate local folder for fetched reference data.

## [0.2.0]

### Added

- `format_list` joins items the way a locale writes a list, from the list patterns of all
  766 locales of Unicode CLDR 48: `conjunction`, `disjunction` and `unit` lists in `long`,
  `short` and `narrow` styles, the vocabulary of `Intl.ListFormat`. `limit` and `more` fold
  a long list into a tail.
- The contextual rules of the ICU list formatter: Spanish `y` to `e` and `o` to `u`, and the
  Hebrew conjunction before a word in another script.
- `ListPattern`, a validated value type with the formatting algorithm, and `list_pattern`
  to read the one of a locale.
- `resolve_locale`, `supported_locales` and `cldr_version`. Tags may be BCP 47 or POSIX;
  deprecated codes, likely scripts and CLDR parent locales are honoured, and an unknown
  language raises `LookupError`.
- `ListType` and `ListStyle` literal types.
- A `humanjoin` command and `python -m humanjoin`.
- The Unicode License v3 ships with the package for the derived CLDR data.

### Changed

- `join_max` takes `conj` and `oxford` and passes them to `join`; before, it always used
  "and" with the Oxford comma.
- `more` may be a callable taking the hidden count, for plurals. A template that uses a
  field other than `{n}` raises `ValueError`.
- Breaking: the argument checks below turn calls that used to return odd text into errors.

### Fixed

- `join_max` raises `ValueError` for a negative limit instead of folding every item into
  the tail, and `TypeError` for a limit that is not an `int` (including `bool`).
- `join` raises `TypeError` for a conjunction that is not a string.

## [0.1.0]

- First release.
- `join` builds a natural-language phrase with a configurable conjunction and an
  optional Oxford comma.
- `join_max` truncates to a limit and folds the rest into a configurable "N more" tail.

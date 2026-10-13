# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
- `more` may be a callable taking the hidden count, for plurals.

### Fixed

- `join_max` raises `ValueError` for a negative limit instead of folding every item into
  the tail, and `TypeError` for a limit that is not an `int` (including `bool`).
- `join` raises `TypeError` for a conjunction that is not a string.

## [0.1.0]

- First release.
- `join` builds a natural-language phrase with a configurable conjunction and an
  optional Oxford comma.
- `join_max` truncates to a limit and folds the rest into a configurable "N more" tail.

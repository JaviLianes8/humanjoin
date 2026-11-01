# humanjoin 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. The release branch resumes uncommitted
changes based on main `4080236dbfc64d4afb18f7fddc6e380c1c0461cf` (0.2.0).
No earlier release commits or certification lens reports were present.

Progress:
- [x] Published baseline checked: PyPI 0.2.0 is live
- [x] Public API, docstrings, typing and error review (items 1 to 5)
- [x] Contracts and seeded properties (items 6 and 9)
- [x] Live sources and reference program output (item 7)
- [x] README, GUIDE and dated CHANGELOG (items 11 and 12)
- [x] Version and stable metadata (item 13)
- [ ] Built artifacts, external wheel consumer, PyPI upgrade (items 8 and 14)
- [ ] Every installed supported interpreter (item 10)
- [ ] Final four gates (item 15)
- [ ] Author mutation round (item 18)
- [ ] Independent reviewer (item 16, separate stage)
- [ ] Five independent QA lenses (item 19, separate stage)
- [ ] Release PR and guard; merge and publication are separate stages (item 17)

## API and behavior

The ten public exports of 0.2.0 retain their names, parameter names and defaults.
`__version__` is 1.0.0; the unintended `annotations` attribute is removed.
`ListPattern` remains a frozen hashable dataclass and is now identified publicly
for pickling. CLDR data and valid list outputs are unchanged. Stricter boolean,
tail, locale-length and template validation, bounded error messages, validation
before input consumption and linear list assembly are described in CHANGELOG.
GUIDE defines errors, finite iterable semantics, lookup limits and CLI behavior.

Public examples are executed, including the literal aliases and `ListPattern.format`.
README and GUIDE output comments are checked. Strict typing covers `src` and `tests`.
User iterator, string conversion and callback exceptions deliberately propagate.

## Ground truth

Fetched and regenerated on 2026-11-01 with `scripts/fetch_upstream.py`; all six
manifest sizes and SHA-256 values matched. `tests/upstream/MANIFEST.json` records
exact URLs, revisions, licenses and checksums. Fetched files stay outside the repo
in the selected `HUMANJOIN_UPSTREAM` folder. Missing files cause clean test skips.

- CLDR 48 npm packages: every one of 766 locales and nine type/style combinations
  compared directly to fetched list patterns; the entire shipped table is rederived.
- ICU 78.3 list formatter: contextual patterns checked against fetched source.
- Unicode 17 Scripts.txt: Hebrew script ranges independently parsed and compared.
- ECMA-402 at revision 730ca2b: types, styles and defaults read from fetched text.
- Node 24.18.0, ICU 78.3, CLDR 48.0, Unicode 17.0 run locally: 36,405 list cases,
  1,512 contextual cases and every Unicode scalar for Hebrew hyphen insertion.
  Of the list cases, 24,930 across 545 tags have comparable resolved locales and
  match. Other Node fallbacks are excluded from that comparison and covered by CLDR.
- PyPI JSON fetched live from https://pypi.org/pypi/humanjoin/json: latest 0.2.0.
- Babel comparison verified against https://babel.pocoo.org/en/latest/api/lists.html
  on 2026-11-01: Babel offers locale-dependent list formatting.

## Contracts and robustness

The resumed baseline passed 234 tests, with one optional wheel test skipped.
The expanded suite pins public signatures, namespace, immutable value behavior,
safe errors, validation timing, template limits and CLI failures. Seeded properties
exercise 6,000 English/overflow cases, 6,000 independently formatted custom lists
and 10,000 hostile locale strings. A 100,000-item test covers English, localized
and reversed wrapped patterns. Hand-written values are identified as such.

## Remaining stages

Items 16 and 19 have not been run for this release. No independent PASS is claimed.
Merge and PyPI publication are not part of preparation.

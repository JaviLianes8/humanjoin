# humanjoin 1.0.0 certification report

Initial preparation for 1.0.0, dated 2026-11-01. The release branch resumes uncommitted
changes based on main `4080236dbfc64d4afb18f7fddc6e380c1c0461cf` (0.2.0).
All nine package files in the downloaded PyPI 0.2.0 wheel equal main byte for byte.
No earlier release commits or certification lens reports were present.
The QA sections below record subsequent findings, fixes and validation.

Progress:
- [x] Published baseline checked: PyPI 0.2.0 is live
- [x] Public API, docstrings, typing and error review (items 1 to 5)
- [x] Contracts and seeded properties (items 6 and 9)
- [x] Live sources and reference program output (item 7)
- [x] README, GUIDE and dated CHANGELOG (items 11 and 12)
- [x] Version and stable metadata (item 13)
- [x] Built artifacts, external wheel consumer, PyPI upgrade (items 8 and 14)
- [x] Every installed supported interpreter (item 10)
- [x] Final four gates (item 15)
- [x] Author mutation round (item 18)
- [ ] Independent reviewer (item 16, separate stage)
- [ ] Five independent QA lenses (item 19, separate stage)
- [x] Release PR #3 and guard CLEAN; merge and publication are separate stages (item 17)

## API and behavior

The ten public exports of 0.2.0 retain their names, parameter names and defaults.
`__version__` is 1.0.0; the unintended `annotations` attribute is removed.
`ListPattern` remains a frozen hashable dataclass and is now identified publicly
for pickling. The 766 locales' list pattern data is unchanged; QA round 1 corrects
alias resolution, variant retention and nonlikely-script inheritance. Stricter boolean,
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
The absent-reference check passes one synthetic test and skips nine reference tests.

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
and 10,000 hostile locale strings, plus 10,000 seeded overflow templates. A
100,000-item test covers English, localized and reversed wrapped patterns.
Hand-written values are identified as such. A separate timing run at 10,000,
40,000 and 160,000 items gave 16x-input ratios of 21.12 (join), 16.49 (localized),
17.07 (reversed wrappers) and 16.10 (truncated), consistent with linear scaling.

## Packaging and upgrade

Built the sdist and then the wheel from that sdist with hatchling 1.33.0.
`twine check --strict` passes for both. The wheel has 16 members: only the
package, CLDR facts, typing marker, entry point, metadata and both licenses.
The sdist has source, tests, manifest, maintenance scripts and user documentation;
no fetched corpus, reference output, process reports, caches or scratch files.

The installed-wheel test builds and installs into a fresh venv, runs a consumer
from an empty folder, and drives both the console executable and `python -m`.
The upgrade test installs actual PyPI 0.2.0, records 41,364 localized results and
21 English/truncation results, upgrades in place, and verifies the digest is
unchanged. It checks documented validation differences, exchanges pickles both
ways with a separate 0.2.0 venv, drives both CLI entry points and runs `pip check`.
A separate consumer passes `mypy --strict` using the installed wheel's type data.

## Available Python interpreters

All work ran locally. Fresh venvs use the built wheel; the test suite is extracted
from the sdist with its `src` directory removed, preventing source-tree imports.
Both the generated console executable and package location are checked.

| Interpreter | Installed-wheel suite | CLI |
| --- | --- | --- |
| CPython 3.14.6 (system installation) | 309 passed, 4 skipped | PASS |
| CPython 3.11.11 (bundled with Blender 4.5.10) | 309 passed, 4 skipped | PASS |

The four skips are two opt-in e2e tests (run separately) and two git-tree checks
that need a checkout. The 13 other `py -0p` entries point to nonexistent files;
all six user Python shims fail because their target interpreter was removed.
Other local venvs use the same system 3.14.6 interpreter. Thus 3.10, 3.12, 3.13
and free-threaded 3.14 could not be run on this PC. They are not claimed tested.

## Author mutation round

22 deliberate changes, one at a time in a disposable local clone, with bytecode
disabled, fetched sources present, `pytest -x` and a 300-second per-test timeout.
Each failed a behavior assertion; none survived. The suite passed before and
after restoration. The separate wheel and PyPI upgrade tests were not rebuilt
for each mutant. The table names the first test that caught each change.

| ID | Mutation | Caught by |
| --- | --- | --- |
| J01 | Omit Oxford comma | `test_docs::test_every_python_example_prints_its_comments` |
| J02 | Reverse two items | `test_docs::test_every_python_example_prints_its_comments` |
| J03 | Accept nonboolean Oxford flag | `test_validation::test_oxford_requires_a_boolean` |
| T01 | Negative limit raises TypeError | `test_cli::test_bad_values_exit_2_with_a_message` |
| T02 | Hidden count off by one | `test_cli::test_limit_and_more` |
| T03 | Add tail at exact length | `test_join::test_join_max_with_the_limit_equal_to_the_length_hides_nothing` |
| T04 | Accept boolean limit | `test_join::test_join_max_rejects_a_limit_that_is_not_an_int` |
| T05 | Drop overflow tail | `test_cli::test_limit_and_more` |
| T06 | Allow excessive format width | `test_validation::test_bad_templates_raise_bounded_value_errors_without_context` |
| P01 | Use start instead of middle | `test_docs::test_guide_examples_print_their_comments` |
| P02 | Drop wrapper prefixes | `test_docs::test_guide_examples_print_their_comments` |
| P03 | Disable Spanish e rule | `test_cli::test_items_from_stdin_skip_blank_lines` |
| P04 | Lose Spanish eleven boundary | `test_intl::test_contextual_spanish_and_hebrew_words_match_intl` |
| P05 | Shift Hebrew range start | `test_intl::test_hebrew_script_ranges_match_intl_for_every_code_point` |
| P06 | Accept duplicate placeholders | `test_pattern::test_each_pattern_needs_both_placeholders_exactly_once` |
| L01 | Unknown locale raises ValueError | `test_intl::test_every_list_length_type_and_style_matches_intl` |
| L02 | Drop POSIX script modifiers | `test_docs::test_guide_examples_print_their_comments` |
| L03 | Accept 256-character locale | `test_validation::test_locale_length_boundary_is_checked_before_ignored_suffixes` |
| F01 | Ignore style index | `test_cli::test_locale_type_and_style_options` |
| F02 | Ignore localized truncation | `test_cli::test_limit_and_more` |
| C01 | CLI success returns one | `test_cli::test_items_from_arguments_default_to_english` |
| C02 | Keep blank stdin lines | `test_cli::test_items_from_stdin_skip_blank_lines` |

## Preparation gates and scorecard

Each command exits 0 independently: `ruff format --check .` (31 files),
`ruff check .`, `mypy --strict src` (8 files), `mypy --strict src tests` (23 files),
and `pytest` (313 passed, no skips, 33.62 seconds). The last command enables
`HUMANJOIN_E2E=1`, `HUMANJOIN_UPGRADE=1`, `HUMANJOIN_WHEEL` and the fetched sources.
Every test has a 300-second timeout and all temporary directories are explicit.

| Item | Preparation result |
| --- | --- |
| 1 | PASS: stable signatures and behavior changes documented |
| 2 | PASS: exact exports and namespace, public imports in examples |
| 3 | PASS: every public name and format method has executed examples |
| 4 | PASS: strict source/tests and installed consumer, typing marker shipped |
| 5 | PASS: documented built-in error families and bounded validation messages |
| 6 | PASS: full public contract, CLI, locale data and value semantics |
| 7 | PASS: live-fetched references and locally executed independent formatter |
| 8 | PASS: wheel consumer, both CLI entry points and live PyPI upgrade |
| 9 | PASS: seeded properties, hostile templates/locales and large-list scaling |
| 10 | PASS for every available interpreter; unavailable versions listed above |
| 11 | PASS: README problem, comparison, absolute links, guide and strict twine check |
| 12 | PASS: CHANGELOG 1.0.0 dated 2026-11-01 |
| 13 | PASS: 1.0.0, Production/Stable, 3.10 to 3.14, licenses, URLs, no runtime dependencies |
| 14 | PASS: sdist and wheel contents inspected, both licenses included |
| 15 | PASS: four gates each exit 0 |
| 16 | Pending separate independent review |
| 17 | PR #3 open from `release/1.0.0`, guard CLEAN; merge and publication pending |
| 18 | PASS: all 22 author mutations killed |
| 19 | Round 7 fix below; independent verification remains pending |

## QA lenses, round 1

Reviewed base: `fe89fa7462623d96201b11d2b97d91560c892302`.
Fix commit: `86df0018210d00b1db6998be07a9702e2df59cb0`
(`fix validation and locale fallback contracts`), pushed on 2026-11-01.

All ten supplied findings are addressed. Each behavior defect had a new failing
contract before its fix: the initial regression run produced 53 failures and 41
passes on the reviewed base. E-01 and E-02 concern missing contracts for existing
behavior; their new tests pass on pristine code and fail with the reported mutations.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| A-001, B-04, C-01 | Bound every Unicode decimal width/precision before formatting, including mixed alphabets and long zero prefixes | `test_tail_unicode.py`, `test_cli_contracts.py`: 10000 accepted, 10001 rejected through both functions and the CLI; numeric fill characters preserved |
| B-01 | Retain compound CLDR aliases in the derived table and apply them before fallback, preserving explicit fields | `test_locale_aliases.py`: all four reported aliases, POSIX/case/extension forms, explicit scripts/regions and Nynorsk unit output |
| B-02 | Retry the complete variant locale after default-script normalization | `test_locale_aliases.py`: Catalan Valencia with BCP 47 and POSIX scripts; numeric variant fallback |
| B-03 | Derive likely scripts for every supported language and apply CLDR's programmatic root parent rule | `test_locale_aliases.py`: Russian, German, English and French nonlikely scripts; unknown languages still raise; direct locale data remains authoritative |
| C-02 | Normalize option subclasses using base-class operations before validation, caching or formatting, including custom pattern fields | `test_option_subclasses.py`: overridden comparison, conversion, length, hash, formatting and pattern operations cannot bypass validation or run hooks |
| C-03 | Read stdin lazily, after semantic options are validated | `test_cli_contracts.py`: invalid limit/locale exits 2 with an open pipe and never reads an instrumented finite stream; template syntax stays deferred |
| E-01 | Assert exact whitespace-bearing argument output bytes through both entry points | `test_cli_contracts.py`, `test_e2e_wheel.py`: M54 fails the module contract and installed-wheel checks for both commands |
| E-02 | Document and pin eager callback-result conversion followed by item coercion | `test_tail_unicode.py`: M14 fails both `join_max` and `format_list` at limit zero; production behavior retained |

The CHANGELOG records every behavior change; GUIDE explains option normalization,
Unicode bounds, corrected locale lookup, CLI validation timing and callable tails.
Public names, signatures and defaults are unchanged. No findings are disputed.

Validation on CPython 3.14.6, with a 300-second per-test timeout:

- `ruff format --check .`: exit 0, 37 files.
- `ruff check .`: exit 0.
- `mypy --strict src`: exit 0, 10 files. Strict source-and-test checks also pass (29 files).
- `pytest`: exit 0, 411 passed with no skips, including installed-wheel and live
  PyPI 0.2.0 upgrade checks. All six freshly fetched/generated reference files match
  their manifest hashes. Both distribution files pass `twine check --strict`.
- All 98 new regression cases pass against a separate clean wheel installation,
  with source-path injection disabled and the import location checked.
- M14 and M54 were replayed separately in disposable copies. M14 causes two
  callable-tail failures; M54 fails the module test and the installed-wheel test
  after exercising both CLI commands. No source changes remain from mutation runs.

CLDR list pattern records and all 766 direct locale entries remain identical.
The corrected `en-Cyrl` inheritance selects root while Node negotiates English;
that probe is no longer a comparable Node case. The other 24,885 comparable
cases across 544 tags pass, and CLDR-derived contracts cover the root behavior.
Evidence logs and disposable environments are under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r1/`.
Independent same-lens verification is still pending; these fix checks do not
claim a new independent PASS verdict.

## QA lenses, round 2

Reviewed base: `8737287b4fc20583dd66efbdb401bf5fad264d66`.
Fix commit: `2be89fbcd0d9734e17c6bd77954baff8c640793b`
(`fix alias precedence and variant fallback contracts`), pushed on 2026-11-01.

All eight supplied findings are addressed. Before production edits, the new
contracts produced 18 failures and 50 passes on the reviewed base. Those failures
cover every reported behavior defect, including both truncating functions for
C-02. E-03, E-04 and E-06 add contracts for existing correct behavior. E-05 pins
the corrected fallback policy shared with B-07. No findings are disputed.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| B-05 | Order aliases by populated CLDR fields, treating `und` as an empty language; restart after each match | `test_alias_rules_repeat_in_field_precedence_order` covers `nor-nynorsk`, `nor-bokmal`, `aar-saaho`, explicit scripts, POSIX and extensions; `test_chained_alias_selects_nynorsk_unit_patterns` requires `A B C` |
| B-06 | Search available variant combinations before the base, including after default-script removal; avoid enumerating nonexistent subsets | `test_variant_combinations_precede_base_fallback` covers both variant orders and all three shipped variant locales; synthetic entries pin count/alphabetical precedence; 38 unrelated variants retain `be-tarask` |
| B-07 | Walk likely-script fallback for default and nondefault scripts, retaining regional entries and explicit parents | `test_unavailable_variants_keep_likely_script_region` covers Singapore, Taiwan, Serbian and Portuguese fallback |
| C-02 | Inspect the actual limit type before `int.__int__` normalization | `test_integer_validation_does_not_read_class_property` rejects a negative subclass before iteration and accepts a positive subclass without reading its raising `__class__` property |
| E-03 | Pin initial BOM removal and noninitial U+FEFF preservation as exact bytes | Source module contracts and installed-wheel subprocesses exercise both entry points, with and without an initial BOM |
| E-04 | Require the source language for compound aliases while retaining language-independent `und` rules | `test_compound_alias_requires_its_source_language` keeps `en-nynorsk`, `en-bokmal`, `en-saaho` and `en-lojban` English and resolves `sv-aaland` to `sv-AX` |
| E-05 | Define unmatched-variant fallback consistently: `zh-SG-1996` now selects `zh-Hans-SG`, as does `zh-SG-fonipa` | Real-data assertions pin that choice; a labeled synthetic `zh-Hans-SG-1996` entry proves script insertion must preserve available variant data |
| E-06 | Pin retention of unrelated variants through language aliases | `test_language_alias_preserves_unrelated_variants` covers `cat-ES-valencia`, its explicit-script form and `bel-tarask` |

CLDR 48 references were fetched again, and all six downloaded/generated files
match their manifest hashes. The matching
[canonicalization and inheritance specification](https://www.unicode.org/reports/tr35/tr35-76/tr35.html)
was fetched on 2026-11-01. Live Node 24.18.0 canonicalizes the three B-05 inputs
to `nn`, `nb` and `ssy`, and produces `A B C` for the reported Nynorsk unit case.
GUIDE, the locale docstring and CHANGELOG describe the corrected behavior.
Public names, signatures, defaults and all 766 direct locale entries are unchanged.

The four surviving mutations were replayed individually in a disposable copy:

| Mutation | Detecting contract | Result |
| --- | --- | --- |
| N22 | `test_module_cli_preserves_noninitial_bom_bytes`; `test_installed_wheel_end_to_end` | Two source failures and one wheel-test failure; both installed commands execute before the byte comparison |
| N27 | `test_compound_alias_requires_its_source_language` | Four failures; the language-independent alias still passes |
| N34 | `test_likely_script_preserves_available_variant_data` | One failure; seven real-data fallback cases pass under the newly documented policy |
| N36 | `test_language_alias_preserves_unrelated_variants` | Three failures |

The 70 targeted tests pass before mutation and after byte-for-byte restoration.
Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths: `ruff format --check .` (38 files), `ruff check .`,
`mypy --strict src` (10 files), and `pytest` all exit 0. Strict typing of both
source and tests also passes (30 files). The full suite has 449 passes and zero
skips with installed-wheel, both CLI entry points, fetched references and live
PyPI 0.2.0 upgrade checks enabled. Evidence is retained under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r2/`.
Independent same-lens verification remains a separate stage; these fix checks
do not claim new independent PASS verdicts.

## QA lenses, round 3

Reviewed base: `57efb3c85cb1cf18941e8d768ef7141a67ed8d7c`.
Fix commit: `1ee009242e84b59527ba216eb9d4a942fcd26744`
(`fix text validation and invalid-limit contracts`), dated 2026-11-01.

Both supplied findings are addressed. Before production edits, the new contracts
produced 14 failures and two passes on the reviewed base. All failures exercise
C-03 through the shared text-option helper. E-07 concerns missing contracts for
already-correct limit validation; its two new tests pass on pristine code and
fail under the reported P20 mutation. No findings are disputed.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| C-03 | Check actual string ancestry before base-class normalization, without reading a supplied `__class__` property | `test_text_options_reject_bytes_without_reading_class_property`: 14 cases cover locales, list types/styles, conjunctions and custom pattern fields; exact `TypeError` messages, no exception context, zero property reads and untouched item iterators |
| E-07 | Retain actual-type limit validation and add contracts for noninteger inputs with raising `__class__` properties | `test_noninteger_limit_is_rejected_without_reading_class_property`: both `join_max` and `format_list` reject the input before property access or iteration |

The positive string-subclass contracts now also include a raising `__class__`
property. All 30 targeted option contracts pass. In a disposable source copy,
P20 changes the limit ancestry check back to `isinstance`: both new limit
contracts fail, while the 14 text-option cases pass. All 16 new contracts pass
before the mutation and after byte-for-byte restoration.

Copies of the supplied reviewer probes pass against the fix: all 40 lens C
sweep cases and both lens E limit witnesses. Original reviewer artifacts remain
unchanged. CHANGELOG records the text-validation behavior change and added limit
contracts. Public names, signatures and defaults remain unchanged.

Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths. Each required gate exits 0: `ruff format --check .` (39 files),
`ruff check .`, `mypy --strict src` (10 files), and `pytest` (465 passed, zero
skips). Strict typing of source and tests also passes (31 files). The full suite
includes installed-wheel checks, both CLI entry points and the live PyPI 0.2.0
upgrade. All six freshly fetched/generated reference files match their manifest
hashes. Logs, mutation results and copied probes are retained under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r3/`.
Independent same-lens verification remains a separate stage; these checks do
not claim new independent PASS verdicts.

## QA lenses, round 4

Reviewed base: `a658ffd77407add18c22c25f0fecd6601e05872c`.
Fix commit: `8095410920f810551fdf2489d4a808500e3cc5c0`
(`add whitespace preservation contracts`), dated 2026-11-01.

E-08 is addressed. It concerns a missing contract for already-correct behavior:
the 48 new tests pass on the reviewed implementation and fail under S08.
Base-string normalization still preserves the exact text. Production code,
public names, signatures, defaults and behavior remain unchanged. No findings
are disputed. CHANGELOG records the added contracts.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| E-08 | Preserve significant option whitespace through both joiners and every custom pattern field; require exact language values for contextual rewriting | `test_option_whitespace.py`: plain strings and subclasses cover spaces, tabs, newlines, nonbreaking spaces, overflow, both Oxford settings, repeated middle patterns and padded `es`, `he` and `iw` values |

The reported mutation was replayed in a disposable source copy with fresh
processes and bytecode writes disabled:

| Mutation | Detecting contracts | Result |
| --- | --- | --- |
| S08: append `.strip()` to base-string normalization | `test_joiners_preserve_conjunction_whitespace`, `test_overflow_preserves_conjunction_whitespace`, `test_custom_pattern_fields_preserve_whitespace`, `test_padded_language_values_keep_patterns_literal` | All 48 new cases fail; all seven copied reviewer whitespace witnesses also fail |

All 55 cases pass before mutation and after byte-for-byte restoration. Original
reviewer artifacts remain unchanged. The new expected values are hand-written
from the public formatting contract.

Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths. Each required gate exits 0: `ruff format --check .` (40 files),
`ruff check .`, `mypy --strict src` (10 files), and `pytest` (513 passed, zero
skips). Strict typing of source and tests also passes (32 files). The full suite
includes installed-wheel checks, both CLI entry points and the live PyPI 0.2.0
upgrade. All six freshly fetched/generated reference files match their manifest
hashes. Logs, the mutation patch and results, and copied witnesses are retained
under `C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r4/`.
Independent same-lens verification remains a separate stage; these checks do
not claim a new independent PASS verdict.

## QA lenses, round 5

Reviewed base: `6fa16146bf8e6aa81b3df27defc0fb4a05962479`.
Fix commit: `172cde49c83148467d051c5f79f63840c7f26a38`
(`add literal text and selector contracts`), dated 2026-11-01.

E-09 through E-13 are addressed. All five findings concern missing contracts
for already-correct behavior. The 256 new cases pass on the reviewed code and
catch every reported mutation. Production code, public names, signatures,
defaults and behavior are unchanged. No findings are disputed. CHANGELOG
records the added contracts, whose expected values are hand-written.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| E-09 | Preserve CRLF in conjunctions and custom pattern fields | `test_option_text.py` covers both joiners, both Oxford settings, overflow, all four fields and repeated middle patterns; stored fields and output retain exact code points |
| E-10 | Preserve decomposed Unicode in text options | The same contracts use `e\u0301`; additional cases preserve overflow-template output and stored custom language text |
| E-11 | Preserve custom language case and select contextual rules by exact code | `test_pattern_language.py` covers lowercase, uppercase and both mixed-case forms of `es`, `he` and `iw`, including Spanish conjunction/disjunction and Hebrew hyphen rules in two-item and longer lists |
| E-12 | Reject padded locale tags across public locale functions | `test_option_selectors.py` covers `resolve_locale`, `list_pattern` and `format_list`, including warmed valid lookups and rejection before item iteration |
| E-13 | Reject padded type and style selectors | Both `list_pattern` and `format_list` reject all three types and styles with leading, trailing or surrounding spaces, tabs, CRLF and nonbreaking spaces; invalid formatting options never start iteration |

Every new contract covers plain strings and string subclasses whose `__str__`
raises. The five exact reviewer patches were replayed serially in a disposable
source copy with fresh processes and bytecode writes disabled:

| Mutation | Detecting contracts | Result |
| --- | --- | --- |
| N06: normalize CRLF to LF | `test_joiners_preserve_conjunction_code_points`, `test_overflow_preserves_conjunction_code_points`, `test_custom_pattern_fields_preserve_code_points`, `test_custom_language_preserves_code_points` | 18 failures |
| N07: normalize text options to NFC | The same exact-code-point contracts with decomposed Unicode | 18 failures |
| N08: lowercase custom language | `test_custom_language_preserves_case_and_selects_exact_contextual_rules` | 24 failures |
| N09: strip locale padding | `test_locale_lookups_reject_padded_tags`, `test_format_list_rejects_padded_locale_before_iteration` | 60 failures |
| N10: strip type/style padding | `test_list_functions_reject_padded_types`, `test_list_functions_reject_padded_styles` | 120 failures |

All 256 cases pass before mutation and after byte-for-byte restoration. There
are no collection errors or skips in any replay. Original reviewer artifacts
remain unchanged.

Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths. Each required gate exits 0: `ruff format --check .` (43 files),
`ruff check .`, `mypy --strict src` (10 files), and `pytest` (769 passed, zero
skips). Strict typing of source and tests also passes (35 files). The full suite
includes installed-wheel checks, both CLI entry points and the live PyPI 0.2.0
upgrade. All six freshly fetched/generated reference files match their manifest
hashes. Gate logs, mutation patches and results are retained under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r5/`.
Independent same-lens verification remains a separate stage; these checks do
not claim a new independent PASS verdict.

## QA lenses, round 6

Reviewed base: `d9b0fe829b3d6c6b9127ee27a07884d9513fdc63`.
Fix commit: `f4c96d1e2f71b3d8bd8d4671469c3292b0a80536`
(`add nul bom language and selector contracts`), dated 2026-11-01.

E-14 through E-18 are addressed. All five findings concern missing contracts
for already-correct behavior. The 146 added cases pass on the reviewed
implementation and catch every reported mutation. Production code, public
names, signatures, defaults and behavior remain unchanged. No findings are
disputed. CHANGELOG records the added contracts; expected values are hand-written.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| E-14 | Preserve embedded NULs in text options | `test_option_text.py` checks exact conjunction output through both joiners, both Oxford settings and overflow; all four custom pattern fields, repeated middle patterns, overflow templates and stored custom language values retain NULs |
| E-15 | Preserve leading BOMs in text options | The same contracts retain U+FEFF in conjunctions, stored pattern fields, pattern output, overflow templates and custom language text |
| E-16 | Keep custom language subtags literal without contextual rules | `test_custom_language_subtags_stay_literal_without_contextual_rules` covers region, script and combined suffixes with hyphens and underscores for `es`, `he` and `iw`; stored values and two-item/longer outputs remain literal for Spanish conjunction/disjunction and Hebrew hyphen rules |
| E-17 | Keep empty custom language strings distinct from `None` | `test_empty_custom_language_remains_a_string_distinct_from_none` checks the exact built-in string type, value inequality and inactive contextual rules |
| E-18 | Reject uppercase and mixed-case type/style selectors | `test_list_functions_reject_nonlowercase_types` and `test_list_functions_reject_nonlowercase_styles` cover all three types and styles through both public list functions, after valid lookups; `format_list` rejects them before item iteration |

Every added contract covers plain strings and subclasses whose `__str__` raises.
The five exact reviewer mutations were replayed serially in a disposable source
copy, with fresh processes and bytecode writes disabled. Each supplied public
witness changed under its mutation, confirming non-equivalence.

| Mutation | Detecting contracts | Result |
| --- | --- | --- |
| S02: remove NULs from text options | `test_joiners_preserve_conjunction_code_points`, `test_overflow_preserves_conjunction_code_points`, `test_custom_pattern_fields_preserve_code_points`, `test_custom_language_preserves_code_points` | 18 failures |
| S03: remove leading BOMs from text options | The same exact-code-point contracts with leading U+FEFF | 18 failures |
| S04: take the primary subtag of custom language values | `test_custom_language_subtags_stay_literal_without_contextual_rules` | 24 failures |
| S05: coerce empty custom language strings to `None` | `test_empty_custom_language_remains_a_string_distinct_from_none` | 6 failures |
| S07: lowercase type/style selectors | `test_list_functions_reject_nonlowercase_types`, `test_list_functions_reject_nonlowercase_styles` | 48 failures |

All 402 targeted cases pass before mutation and after byte-for-byte source
restoration. Completed replays have no collection errors, timeouts or skips.
Original reviewer artifacts remain unchanged.

Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths. Each required gate exits 0: `ruff format --check .` (43 files),
`ruff check .`, `mypy --strict src` (10 files), and `pytest` (915 passed, zero
skips). Strict typing of source and tests also passes (35 files). The full suite
includes installed-wheel checks, both CLI entry points and the live PyPI 0.2.0
upgrade. All six freshly fetched/generated reference files match their manifest
hashes. Gate logs, mutation patches, witnesses and results are retained under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r6/`.
Independent same-lens verification remains a separate stage; these checks do
not claim a new independent PASS verdict.

## QA lenses, round 7

Reviewed base: `859d9cd728014a2e4cdb093dbb01217eba60b8af`.
Fix commit: `520d5d93d8737fd032d090614a923e0983ef7c49`
(`add surrogate preservation contracts`), dated 2026-11-01.

E-19 is addressed. It concerns a missing contract for already-correct behavior.
The 44 added cases pass on the reviewed implementation and catch the reported
lossy UTF-8 mutation. Production code, public names, signatures, defaults and
behavior remain unchanged. No findings are disputed. CHANGELOG records the added
contracts; expected values are hand-written and compared directly as Python strings.

| Finding | Change | Regression evidence |
| --- | --- | --- |
| E-19 | Preserve lone high and low surrogates in text options | `test_option_text.py` covers exact conjunction output through both joiners, both Oxford settings and overflow; overflow templates, all four custom pattern fields, repeated middle patterns and stored custom language values preserve code points and literal output |

Every added contract covers plain strings and subclasses whose `__str__` raises.
The exact reviewer mutation was replayed in a disposable source copy with fresh
processes and bytecode writes disabled. The public witness changes from
`"a x\ud800y b"` to `"a x?y b"`; a lone low surrogate also becomes `?`.

| Mutation | Detecting contracts | Result |
| --- | --- | --- |
| N02: encode text options as UTF-8 with replacement, then decode | `test_joiners_preserve_conjunction_code_points`, `test_overflow_preserves_conjunction_code_points`, `test_custom_pattern_fields_preserve_code_points`, `test_custom_language_preserves_code_points` | 36 failures, 96 passes; no collection errors, timeouts or skips |

All 132 targeted cases pass before mutation and after byte-for-byte source
restoration. Original reviewer artifacts remain unchanged.

Validation on CPython 3.14.6 uses a 300-second per-test timeout and scratch-only
temporary paths. Each required gate exits 0: `ruff format --check .` (43 files),
`ruff check .`, `mypy --strict src` (10 files), and `pytest` (959 passed, zero
skips). Strict typing of source and tests also passes (35 files). The full suite
includes installed-wheel checks, both CLI entry points and the live PyPI 0.2.0
upgrade. All six freshly fetched/generated reference files match their manifest
hashes. Gate logs, the mutation patch, witnesses and results are retained under
`C:/lianes8-build/codex-pylib/scratch/humanjoin-cert/fix-r7/`.
Independent same-lens verification remains a separate stage; these checks do
not claim a new independent PASS verdict.

## Remaining stages

Item 16 remains a separate review stage. The round 7 finding for item 19 is fixed
above and awaits independent verification. No new independent PASS is claimed.
Merge and PyPI publication are not part of preparation.
The release PR is https://github.com/JaviLianes8/humanjoin/pull/3.

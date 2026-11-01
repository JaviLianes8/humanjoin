# humanjoin 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. The release branch resumes uncommitted
changes based on main `4080236dbfc64d4afb18f7fddc6e380c1c0461cf` (0.2.0).
All nine package files in the downloaded PyPI 0.2.0 wheel equal main byte for byte.
No earlier release commits or certification lens reports were present.

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

## Final gates and scorecard

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
| 17 | Release PR and guard pending; merge and publication are separate stages |
| 18 | PASS: all 22 author mutations killed |
| 19 | Pending separate QA lenses a, b, c, d and e |

## Remaining stages

Items 16 and 19 have not been run for this release. No independent PASS is claimed.
Merge and PyPI publication are not part of preparation.

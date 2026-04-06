# Tasks: Fix Zotero Word Concatenation

**Input**: Design documents from
`/specs/007-fix-zotero-word-concat/`
**Prerequisites**: plan.md, spec.md, research.md,
data-model.md, contracts/

**Tests**: Required (Constitution Principle III: Test-First).

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

+ **[P]**: Can run in parallel (different files, no
  dependencies)
+ **[Story]**: Which user story this task belongs to
  (US1, US2)
+ Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Create the new word fixer module file. No new
project structure needed — existing `src/otb/` layout is
already in place.

+ [X] T001 Create empty `src/otb/word_fixer.py` with module
  docstring and imports for `subprocess`, `shutil`, `sys`,
  `re`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The aspell availability check and core
splitting logic are needed by both user stories.

+ [X] T002 Write failing test for `check_aspell_available()`
  in `tests/test_word_fixer.py`: mock `shutil.which` to
  return `None`, assert `RuntimeError` is raised with
  installation instructions; mock it to return a path,
  assert no error
+ [X] T003 Implement `check_aspell_available()` in
  `src/otb/word_fixer.py`: use `shutil.which("aspell")`,
  raise `RuntimeError` with message including
  `brew install aspell` if not found
+ [X] T004 Write failing test for basic word splitting in
  `tests/test_word_fixer.py`: call
  `fix_concatenated_words(["isthat is fine"])`, assert
  result text contains "is that is fine" and fix count is 1
+ [X] T005 Write failing test for legitimate words in
  `tests/test_word_fixer.py`: call
  `fix_concatenated_words(["cannot without into himself"])`,
  assert text is unchanged and fix count is 0
+ [X] T006 Write failing test for allowlisted words in
  `tests/test_word_fixer.py`: call with text containing
  "superclass" and "codebase", assert they are not split
+ [X] T007 Write failing test for empty input in
  `tests/test_word_fixer.py`: call
  `fix_concatenated_words([])`, assert returns empty list
  and fix count 0
+ [X] T008 Implement `fix_concatenated_words(texts:
  list[str], verbose: bool = False) -> tuple[list[str],
  int]` in `src/otb/word_fixer.py`:
  collect unique tokens across all texts, run
  `aspell list` to find misspelled words, run `aspell -a`
  to get suggestions, filter by allowlist and minimum
  3-char halves, build replacement map, apply to texts,
  return cleaned texts and fix count. Print individual
  fixes to stderr when verbose is True.
+ [X] T009 Verify all foundational tests pass:
  `uv run pytest tests/test_word_fixer.py`

**Checkpoint**: Word fixer module works standalone. aspell
availability check and core splitting logic verified.

---

## Phase 3: User Story 1 — Automatic Word Splitting (P1) MVP

**Goal**: Integrate word-splitting into the Zotero parse
pipeline so annotation text is clean when written to output.

**Independent Test**: Run `otb zotero parse` on the fixture
directory and verify known concatenated words are split in
the output files.

### Tests for User Story 1

> **Write these tests FIRST, ensure they FAIL before
> implementation.**

+ [X] T010 [P] [US1] Write failing test for word splitting
  in parsed output in `tests/test_zotero_parser.py`: parse
  the fixture directory, find an annotation that originally
  contained "SoftwareWithout" (or similar known
  concatenation), assert the parsed text contains
  "Software Without"
+ [ ] T011 [P] [US1] Write failing test for annotation
  count preservation in `tests/test_zotero_parser.py`:
  assert annotation count is still 306 after word-splitting
  is applied (splitting must not add or remove annotations)
+ [ ] T012 [P] [US1] Write failing test for fix count
  summary in `tests/test_zotero_parser.py`: parse the
  fixture directory with capsys/capfd, assert stderr
  contains "Fixed" and a number
+ [ ] T013 [P] [US1] Write failing test for aspell not
  found in `tests/test_zotero_parser.py`: mock
  `shutil.which` to return `None`, assert
  `parse_zotero_annotations()` raises `RuntimeError`
+ [ ] T014 [P] [US1] Write failing CLI test for default
  summary output in `tests/test_cli_zotero.py`: invoke
  `otb zotero parse <fixture-dir> <tmp-dir>`, assert
  stderr contains "Fixed" (the summary line)
+ [ ] T015 [P] [US1] Write failing CLI test for aspell
  not found in `tests/test_cli_zotero.py`: mock
  `shutil.which` to return `None`, invoke the CLI, assert
  exit code 1 and error message mentions aspell

### Implementation for User Story 1

+ [ ] T016 [US1] Integrate word fixer into
  `src/otb/zotero_parser.py`: import
  `check_aspell_available` and `fix_concatenated_words`,
  call `check_aspell_available()` at the start of
  `parse_zotero_annotations()`, after regex extraction
  collect all annotation texts, call
  `fix_concatenated_words()`, apply cleaned texts back,
  print fix count summary to stderr
+ [ ] T017 [US1] Update `src/otb/cli.py` to catch
  `RuntimeError` from aspell availability check: in the
  `zotero_parse` command, catch `RuntimeError` alongside
  `FileNotFoundError`, print to stderr, exit with code 1
+ [ ] T018 [US1] Verify all US1 tests pass:
  `uv run pytest tests/test_zotero_parser.py tests/test_cli_zotero.py tests/test_word_fixer.py`

**Checkpoint**: Core feature works end-to-end. Parsed
annotations have clean, readable text.

---

## Phase 4: User Story 2 — Verbose Review Mode (P2)

**Goal**: Add `--verbose` flag to show individual word
splits.

**Independent Test**: Run with `--verbose` and verify each
split is reported individually on stderr.

### Tests for User Story 2

+ [X] T019 [P] [US2] Write failing test for verbose output
  in `tests/test_word_fixer.py`: call
  `fix_concatenated_words(["isthat"], verbose=True)` with
  capsys/capfd, assert stderr contains "'isthat'" and
  "'is that'"
+ [ ] T020 [P] [US2] Write failing CLI test for `--verbose`
  flag in `tests/test_cli_zotero.py`: invoke
  `otb zotero parse --verbose <fixture-dir> <tmp-dir>`,
  assert stderr contains individual split reports

### Implementation for User Story 2

+ [ ] T021 [US2] Add `--verbose` option to
  `src/otb/cli.py`: add `@click.option("--verbose",
  is_flag=True)` to the `zotero_parse` command, pass it
  through to `parse_zotero_annotations()`
+ [ ] T022 [US2] Update `parse_zotero_annotations()` in
  `src/otb/zotero_parser.py`: accept `verbose: bool =
  False` parameter, pass it to `fix_concatenated_words()`
+ [ ] T023 [US2] Verify all US2 tests pass:
  `uv run pytest tests/test_word_fixer.py tests/test_cli_zotero.py -k "verbose"`

**Checkpoint**: Users can review individual word splits.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates and final validation.

+ [X] T024 [P] Run full test suite: `uv run pytest`
+ [ ] T025 [P] Run type checker: `uv run mypy src/ tests/`
+ [ ] T026 [P] Run linter: `uv run pylint src/ tests/`
+ [ ] T027 [P] Run markdown linter:
  `pymarkdownlnt scan "**/*.md"`
+ [ ] T028 Run quickstart.md validation: execute the
  commands from
  `specs/007-fix-zotero-word-concat/quickstart.md` and
  verify they work as documented

---

## Dependencies & Execution Order

### Phase Dependencies

+ **Setup (Phase 1)**: No dependencies
+ **Foundational (Phase 2)**: Depends on Phase 1
+ **US1 (Phase 3)**: Depends on Phase 2 (word fixer module)
+ **US2 (Phase 4)**: Depends on Phase 3 (parser integration
  exists)
+ **Polish (Phase 5)**: Depends on all prior phases

### User Story Dependencies

+ **US1 (P1)**: Depends on foundational word fixer module.
  Core feature; must complete before US2.
+ **US2 (P2)**: Extends US1 with verbose output. Can only
  start after US1 parser integration exists.

### Within Each User Story

+ Tests MUST be written and FAIL before implementation
+ Module functions before CLI wiring
+ Core implementation before verbose mode
+ Story complete before moving to next priority

### Parallel Opportunities

+ T010-T015 (all US1 tests) can be written in parallel
+ T019-T020 (all US2 tests) can be written in parallel
+ T024-T027 (quality gates) can all run in parallel

---

## Parallel Example: User Story 1

```text
# Write all US1 tests in parallel:
T010: Test word splitting in parsed output
T011: Test annotation count preservation
T012: Test fix count summary
T013: Test aspell not found
T014: CLI default summary output
T015: CLI aspell not found

# Then implement sequentially:
T016: Parser integration → T017: CLI error handling → T018: Verify
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T009)
3. Complete Phase 3: User Story 1 (T010-T018)
4. **STOP and VALIDATE**: Test US1 independently
5. Zotero parsing with clean text is ready to use

### Incremental Delivery

1. Setup + Foundational → Word fixer module works
2. Add US1 → Parser integration works (MVP!)
3. Add US2 → Verbose review mode available
4. Polish → All quality gates pass

---

## Notes

+ [P] tasks = different files, no dependencies
+ [Story] label maps task to specific user story
+ Constitution Principle III requires test-first: red-green
+ Commit after each task or logical group
+ Stop at any checkpoint to validate story independently
+ aspell is a system dependency; tests that call aspell
  directly require it to be installed on the CI/dev machine

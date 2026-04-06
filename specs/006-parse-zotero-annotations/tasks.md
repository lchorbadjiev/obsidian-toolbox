# Tasks: Parse Zotero Annotations

**Input**: Design documents from
`/specs/006-parse-zotero-annotations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/

**Tests**: Required (Constitution Principle III: Test-First).

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

+ **[P]**: Can run in parallel (different files, no dependencies)
+ **[Story]**: Which user story this task belongs to (US1, US2)
+ Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. Existing `src/otb/`
layout and `tests/fixtures/zotero/` fixtures are already in place.
This phase creates the new source and test files.

+ [X] T001 Create empty `src/otb/zotero_parser.py` with module
  docstring and imports for `Path`, `Book`, `Annotation` from
  `src/otb/parser.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Parser functions that both user stories depend on.
The book metadata parser is needed by all annotation parsing.

+ [X] T002 Write failing test for `parse_book_metadata()` in
  `tests/test_zotero_parser.py`: given the fixture
  `tests/fixtures/zotero/book.txt`, assert it returns a `Book`
  with title `"Refactoring: Improving the Design of Existing Code"`
  and author `"Martin Fowler"`
+ [X] T003 Implement `parse_book_metadata(path: Path) -> Book`
  in `src/otb/zotero_parser.py`: read alternating label/value
  lines, extract `Title` and `Authors` fields, return `Book`
  dataclass. Raise `FileNotFoundError` if file missing.
+ [X] T004 Write failing test for empty/header-only
  `Annotations.md` in `tests/test_zotero_parser.py`: create a
  temp file with only `# Annotations\n(date)\n`, assert
  `parse_zotero_annotations()` returns an empty list

**Checkpoint**: Book metadata parsing works; empty input handled.

---

## Phase 3: User Story 1 - Parse and Write Annotations (P1) MVP

**Goal**: Parse all annotations from a Zotero export directory
and write each as an individual markdown file in the existing
annotation format.

**Independent Test**: Run `otb zotero parse` on the fixture
directory, verify correct number of output files with valid
frontmatter, titles, and blockquotes.

### Tests for User Story 1

> **Write these tests FIRST, ensure they FAIL before
> implementation.**

+ [X] T005 [P] [US1] Write failing test for
  `parse_zotero_annotations()` annotation count in
  `tests/test_zotero_parser.py`: given the fixture directory
  `tests/fixtures/zotero/`, assert the returned list length
  matches the number of quoted annotations in `Annotations.md`
+ [X] T006 [P] [US1] Write failing test for annotation field
  values in `tests/test_zotero_parser.py`: assert first
  annotation has correct `page`, `location` (= page), `text`
  (quoted content), `title` (auto-generated, up to 7 words),
  `number` (1), `chapter` (empty string), `color` (None),
  and `book` fields matching `book.txt`
+ [X] T007 [P] [US1] Write failing test for sequential numbering
  in `tests/test_zotero_parser.py`: assert all annotations have
  `number` values from 1 to N in order
+ [X] T008 [P] [US1] Write failing test for missing `book.txt`
  in `tests/test_zotero_parser.py`: given a directory with only
  `Annotations.md`, assert `FileNotFoundError` is raised
+ [X] T009 [P] [US1] Write failing CLI test in
  `tests/test_cli_zotero.py`: invoke
  `otb zotero parse <fixture-dir> <tmp-dir>` via `CliRunner`,
  assert exit code 0 and correct number of files written
+ [X] T010 [P] [US1] Write failing CLI test for round-trip in
  `tests/test_cli_zotero.py`: after running the CLI command,
  read output files back with `parse_annotation_dir()` from
  `md_parser.py` and assert they parse without errors
+ [X] T011 [P] [US1] Write failing CLI test for missing input
  in `tests/test_cli_zotero.py`: invoke with a directory
  missing `book.txt`, assert exit code 1 and error on stderr

### Implementation for User Story 1

+ [X] T012 [US1] Implement `parse_zotero_annotations()` in
  `src/otb/zotero_parser.py`:
  read `book.txt` via `parse_book_metadata()`, parse
  `Annotations.md` with regex to extract quoted text and page
  numbers, create `Annotation` objects with auto-generated
  titles using `_title_from_text()` from `parser.py` (make it
  importable if needed), assign sequential numbers, set
  `location = page`
+ [X] T013 [US1] Add `zotero` command group and `parse`
  subcommand in `src/otb/cli.py`: `@main.group()` for
  `zotero`, `@zotero.command("parse")` taking `INPUT_DIR`
  (`click.Path(exists=True, file_okay=False)`) and
  `OUTPUT_DIR` (`click.Path(file_okay=False)`); delegates to
  `parse_zotero_annotations()` then `write_annotations()`;
  prints count to stdout; catches errors and exits with code 1
+ [X] T014 [US1] Verify all US1 tests pass:
  `uv run pytest tests/test_zotero_parser.py tests/test_cli_zotero.py`

**Checkpoint**: Core feature works end-to-end. User can parse
Zotero exports into annotation markdown files.

---

## Phase 4: User Story 2 - Edge Cases (P2)

**Goal**: Handle short fragments, single-word annotations, and
unparseable lines gracefully.

**Independent Test**: Include fragment annotations in test input
and verify valid output; verify unparseable lines produce
warnings.

### Tests for User Story 2

+ [X] T015 [P] [US2] Write failing test for single-word
  annotation in `tests/test_zotero_parser.py`: create a temp
  `Annotations.md` with `"If" ("Book", p. 4)`, assert the
  parsed annotation has text `"If"` and a valid title
+ [X] T016 [P] [US2] Write failing test for short fragment in
  `tests/test_zotero_parser.py`: create a temp file with
  `"your design" ("Book", p. 12)`, assert it parses correctly
  with text `"your design"`
+ [X] T017 [P] [US2] Write failing test for unparseable line
  in `tests/test_zotero_parser.py`: create a temp file with
  a line that has no page reference, assert it is skipped and
  the returned list excludes it

### Implementation for User Story 2

+ [X] T018 [US2] Ensure `parse_zotero_annotations()` in
  `src/otb/zotero_parser.py` handles edge cases: skip lines
  that do not match the annotation regex (print warning to
  stderr), handle single-word and fragment annotations (the
  title generation already handles short text)
+ [X] T019 [US2] Verify all US2 tests pass:
  `uv run pytest tests/test_zotero_parser.py -k "fragment or single or unparseable"`

**Checkpoint**: Parser is robust against real-world Zotero
export quirks.

---

## Phase 5: MCP Tool

**Purpose**: Expose Zotero parsing as an MCP tool per
Constitution Principle VI.

+ [X] T020 [P] Write failing MCP test in
  `tests/test_mcp_server.py`: test `parse_zotero_export` tool
  returns correct annotation dicts for fixture directory; test
  error handling for missing directory
+ [X] T021 Add `parse_zotero_export` tool in
  `src/otb/mcp_server.py`: `@mcp.tool()` decorator, takes
  `path: str`, delegates to `parse_zotero_annotations()`,
  converts results via `_annotation_to_dict()`; raises
  `FileNotFoundError` / `NotADirectoryError` for invalid input
+ [X] T022 Verify MCP test passes:
  `uv run pytest tests/test_mcp_server.py -k "zotero"`

**Checkpoint**: Zotero parsing available via MCP server.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates and final validation.

+ [X] T023 [P] Run full test suite: `uv run pytest`
+ [X] T024 [P] Run type checker: `uv run mypy src/ tests/`
+ [X] T025 [P] Run linter: `uv run pylint src/ tests/`
+ [X] T026 [P] Run markdown linter:
  `npx markdownlint-cli "**/*.md"`
+ [X] T027 Run quickstart.md validation: execute the commands
  from `specs/006-parse-zotero-annotations/quickstart.md` and
  verify they work as documented

---

## Dependencies & Execution Order

### Phase Dependencies

+ **Setup (Phase 1)**: No dependencies
+ **Foundational (Phase 2)**: Depends on Phase 1
+ **US1 (Phase 3)**: Depends on Phase 2 (book metadata parser)
+ **US2 (Phase 4)**: Depends on Phase 3 (core parser exists)
+ **MCP (Phase 5)**: Depends on Phase 3 (parser function exists)
+ **Polish (Phase 6)**: Depends on all prior phases

### User Story Dependencies

+ **US1 (P1)**: Depends on foundational book metadata parser.
  Core feature; must complete before US2.
+ **US2 (P2)**: Extends US1 parser with edge case handling.
  Can only start after US1 core parser exists.
+ **MCP (Phase 5)**: Independent of US2. Can run in parallel
  with US2 after US1 completes.

### Within Each User Story

+ Tests MUST be written and FAIL before implementation
+ Parser functions before CLI wiring
+ Core implementation before edge case handling
+ Story complete before moving to next priority

### Parallel Opportunities

+ T005-T011 (all US1 tests) can be written in parallel
+ T015-T017 (all US2 tests) can be written in parallel
+ T020 (MCP test) can run in parallel with Phase 4 (US2)
+ T023-T026 (quality gates) can all run in parallel

---

## Parallel Example: User Story 1

```text
# Write all US1 tests in parallel:
T005: Test annotation count in tests/test_zotero_parser.py
T006: Test annotation fields in tests/test_zotero_parser.py
T007: Test sequential numbering in tests/test_zotero_parser.py
T008: Test missing book.txt in tests/test_zotero_parser.py
T009: CLI happy path in tests/test_cli_zotero.py
T010: CLI round-trip in tests/test_cli_zotero.py
T011: CLI error handling in tests/test_cli_zotero.py

# Then implement sequentially:
T012: Core parser → T013: CLI command → T014: Verify
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002-T004)
3. Complete Phase 3: User Story 1 (T005-T014)
4. **STOP and VALIDATE**: Test US1 independently
5. Functional Zotero parsing is ready to use

### Incremental Delivery

1. Setup + Foundational -> Book metadata parsing works
2. Add US1 -> Core parsing and CLI work (MVP!)
3. Add US2 -> Edge cases handled robustly
4. Add MCP -> AI agents can use Zotero parsing
5. Polish -> All quality gates pass

---

## Notes

+ [P] tasks = different files, no dependencies
+ [Story] label maps task to specific user story
+ Constitution Principle III requires test-first: red-green
+ Commit after each task or logical group
+ Stop at any checkpoint to validate story independently

# Tasks: Boox Annotation Parser

**Input**: Design documents from `/specs/010-boox-parser/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Phase 1: Setup

**Purpose**: Create test fixtures and project scaffolding

- [x] T001 Create fixture directory `tests/fixtures/boox/`
  and copy `book.txt` from
  `tmp/just-for-fun-torvalds/book.txt`
- [x] T002 Copy Boox annotation file from
  `tmp/just-for-fun-torvalds/` to
  `tests/fixtures/boox/annotations.txt`

**Checkpoint**: Fixture files ready for test-first development

---

## Phase 2: User Story 1 & 2 - Parse Boox Annotations and Handle Multi-line Text (Priority: P1)

**Goal**: Parse a Boox export directory into `list[Annotation]`
with correct book metadata, chapter tracking, page-to-location
mapping, and multi-line text handling.

**Independent Test**: Point parser at `tests/fixtures/boox/`,
verify it returns 30 Annotation objects with correct fields.

### Tests for User Story 1 & 2

> **NOTE: Write these tests FIRST, ensure they FAIL before
> implementation (Constitution III)**

- [x] T003 [P] [US1] Write test `test_parse_book_metadata`
  verifying Book title and author extraction from fixture
  in `tests/test_boox_parser.py`
- [x] T004 [P] [US1] Write test `test_annotation_count`
  verifying 35 annotations from fixture in
  `tests/test_boox_parser.py`
- [x] T005 [P] [US1] Write test `test_first_annotation_fields`
  verifying book, chapter, page (empty string), location
  (int), text, title, color (None) for first annotation in
  `tests/test_boox_parser.py`
- [x] T006 [P] [US1] Write test `test_chapter_tracking`
  verifying annotations have correct chapter headings
  (Roman numerals and full titles) in
  `tests/test_boox_parser.py`
- [x] T007 [P] [US2] Write test `test_multiline_annotation`
  verifying multi-line text is joined into single string
  in `tests/test_boox_parser.py`
- [x] T008 [P] [US1] Write test `test_missing_book_txt`
  and `test_missing_annotation_file` raising
  FileNotFoundError in `tests/test_boox_parser.py`
- [x] T009 [P] [US1] Write test `test_empty_annotation_skipped`
  verifying annotation blocks with no text are skipped
  in `tests/test_boox_parser.py`

### Implementation for User Story 1 & 2

- [x] T010 [US1] Create `src/otb/boox_parser.py` with
  `parse_boox_annotations(directory: Path) -> list[Annotation]`
  implementing the line-based state machine: HEADER →
  BETWEEN → IN_ANNOTATION. Uses own `_parse_book_metadata`
  (handles Boox blank-line format) and `_title_from_text`.
  Map `Page No.` to `location` (int), set `page` to empty
  string, `color` to None.
- [x] T011 [US1] Run `uv run pytest tests/test_boox_parser.py`
  and verify all tests pass (green)
- [x] T012 [US1] Run `uv run mypy src/otb/boox_parser.py` and
  `uv run pylint src/otb/boox_parser.py` — fix any issues

**Checkpoint**: Core parser complete and tested. US1 and US2
independently verifiable via fixture.

---

## Phase 3: User Story 3 - Consistent Numbering (Priority: P2)

**Goal**: Each annotation gets a sequential number starting at 1.

**Independent Test**: Verify `number` fields run 1..N with no
gaps.

### Tests for User Story 3

- [x] T013 [US3] Write test `test_sequential_numbering`
  verifying `[a.number for a in annotations]` equals
  `list(range(1, len(annotations) + 1))` in
  `tests/test_boox_parser.py`

### Implementation for User Story 3

- [x] T014 [US3] Add sequential numbering loop to
  `parse_boox_annotations` in `src/otb/boox_parser.py`
  (assign `a.number = i` for `i` starting at 1)
- [x] T015 [US3] Run `uv run pytest tests/test_boox_parser.py`
  — verify numbering test passes

**Checkpoint**: Parser fully functional with numbered annotations.

---

## Phase 4: CLI & MCP Integration

**Purpose**: Expose the parser via CLI command and MCP tool
(Constitution Principles I and VI)

- [x] T016 [P] Add `otb boox` Click group and `otb boox parse`
  command in `src/otb/cli.py` accepting INPUT_DIR and
  OUTPUT_DIR arguments, delegating to
  `parse_boox_annotations` and `write_annotations`
- [x] T017 [P] Add `parse_boox_export` MCP tool in
  `src/otb/mcp_server.py` accepting `path` string
  parameter, delegating to `parse_boox_annotations`,
  returning list of annotation dicts
- [x] T018 [P] Write CLI integration test in
  `tests/test_cli_boox.py` verifying `otb boox parse`
  produces markdown output from fixture directory
- [x] T019 [P] Write MCP tool test in
  `tests/test_mcp_server.py` verifying `parse_boox_export`
  returns correct annotation count and fields
- [x] T020 Run `uv run pytest` — verify all tests pass
- [x] T021 Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix any issues

**Checkpoint**: Parser accessible via CLI and MCP. All quality
gates pass.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T022 Run `pymarkdownlnt scan -r --respect-gitignore .`
  — fix any markdown lint issues
- [x] T023 Run full quality gate suite:
  `uv run pytest && uv run mypy src/ tests/ && uv run pylint src/ tests/`
- [x] T024 Verify sample export parses correctly:
  `uv run otb boox parse tmp/just-for-fun-torvalds/ /tmp/boox-test-output/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **US1+US2 (Phase 2)**: Depends on Setup (fixtures needed)
- **US3 (Phase 3)**: Depends on US1+US2 (parser must exist)
- **CLI & MCP (Phase 4)**: Depends on US3 (parser complete)
- **Polish (Phase 5)**: Depends on all previous phases

### Within Each Phase

- Tests MUST be written and FAIL before implementation
  (Constitution III)
- Implementation tasks run sequentially within a phase
- Tasks marked [P] can run in parallel

### Parallel Opportunities

- T003-T009: All test-writing tasks can run in parallel
  (same file but independent test functions)
- T016-T019: CLI command, MCP tool, and their tests can
  run in parallel (different files)

---

## Parallel Example: User Story 1 & 2 Tests

```text
# Launch all test-writing tasks together:
Task T003: "test_parse_book_metadata in test_boox_parser.py"
Task T004: "test_annotation_count in test_boox_parser.py"
Task T005: "test_first_annotation_fields in test_boox_parser.py"
Task T006: "test_chapter_tracking in test_boox_parser.py"
Task T007: "test_multiline_annotation in test_boox_parser.py"
Task T008: "test_missing_files in test_boox_parser.py"
Task T009: "test_empty_annotation in test_boox_parser.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (fixtures)
2. Complete Phase 2: US1+US2 (core parser)
3. **STOP and VALIDATE**: Run fixture tests independently
4. Parser is usable from Python code at this point

### Incremental Delivery

1. Setup + US1+US2 → Core parser works (MVP)
2. Add US3 → Annotations are numbered
3. Add CLI + MCP → Parser exposed to users and AI agents
4. Polish → All quality gates green

---

## Notes

- `parse_book_metadata` is reused from `zotero_parser.py`
  (research decision R2)
- No aspell dependency needed (research decision R4)
- `Page No.` maps to `location` (int), `page` is empty string
  (user clarification)
- Annotation file discovered by globbing `*.txt` excluding
  `book.txt` (research decision R3)

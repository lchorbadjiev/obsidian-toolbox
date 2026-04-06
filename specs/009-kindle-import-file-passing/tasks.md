# Tasks: Improve Kindle Import MCP Tools

**Input**: Design documents from
`/specs/009-kindle-import-file-passing/`
**Prerequisites**: plan.md, spec.md, research.md,
data-model.md, contracts/

**Tests**: Included (Constitution Principle III: Test-First).

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no deps)
- **[Story]**: Which user story (US1, US2, US3)
- Exact file paths included in descriptions

---

## Phase 1: Setup

**Purpose**: No new project structure needed. This feature
modifies existing files only.

- [x] T001 Read current implementation in
  src/otb/mcp_server.py to confirm understanding of
  `parse_kindle_export`, `save_annotations`, and
  `kindle_import_annotations`

---

## Phase 2: Foundational

**Purpose**: No foundational/blocking tasks. All changes are
scoped to the MCP server module and its tests. User stories
can proceed directly.

**Checkpoint**: Ready for user story implementation.

---

## Phase 3: User Story 1 - Parse to Temp File (Priority: P1)

**Goal**: `parse_kindle_export` writes annotations to a temp
JSON file and returns a lightweight summary instead of the
full annotation array.

**Independent Test**: Call `parse_kindle_export` on the
existing HTML fixture and verify the response is a dict with
`file_path`, `count`, `book_title`, `author`, `chapters` —
and that the temp file contains the full annotation array.

### Tests for User Story 1

> **Write these tests FIRST, ensure they FAIL before
> implementation**

- [x] T002 [P] [US1] Write test that `parse_kindle_export`
  returns a dict (not a list) with keys `file_path`, `count`,
  `book_title`, `author`, `chapters` in
  tests/test_mcp_server.py
- [x] T003 [P] [US1] Write test that the temp file at
  `file_path` contains valid JSON with 4 annotation dicts
  (using existing fixture) in tests/test_mcp_server.py
- [x] T004 [P] [US1] Write test that `count` equals the
  number of annotations in the temp file in
  tests/test_mcp_server.py
- [x] T005 [P] [US1] Write test that `chapters` contains the
  unique chapter names from the fixture in
  tests/test_mcp_server.py
- [x] T006 [P] [US1] Write test that `parse_kindle_export`
  still raises `FileNotFoundError` for missing paths in
  tests/test_mcp_server.py

### Implementation for User Story 1

- [x] T007 [US1] Refactor `parse_kindle_export` in
  src/otb/mcp_server.py to write annotations to a temp JSON
  file using `tempfile.NamedTemporaryFile(delete=False,
  suffix=".json")` and return a summary dict with
  `file_path`, `count`, `book_title`, `author`, `chapters`
- [x] T008 [US1] Update existing tests in
  tests/test_mcp_server.py that depend on
  `parse_kindle_export` returning a list (update
  `test_parse_returns_annotations`, `test_parse_no_titles`,
  `test_parse_annotation_fields`, `test_parse_empty_export`)
  to work with the new summary dict return type
- [x] T009 [US1] Run `uv run pytest tests/test_mcp_server.py`
  and verify all US1 tests pass
- [x] T010 [US1] Run `uv run mypy src/otb/mcp_server.py` and
  `uv run pylint src/otb/mcp_server.py` — fix any issues

**Checkpoint**: `parse_kindle_export` returns a summary and
writes temp file. All tests green. Mypy and pylint clean.

---

## Phase 4: User Story 2 - Save From File Path (Priority: P2)

**Goal**: `save_annotations` accepts a `file_path` parameter
as an alternative to `annotations`, with mutual exclusion.

**Independent Test**: Create a temp JSON file with annotation
dicts, call `save_annotations(file_path=X, directory=Y)`,
and verify all markdown files are written. Also verify
backward compat with inline `annotations` parameter.

### Tests for User Story 2

> **Write these tests FIRST, ensure they FAIL before
> implementation**

- [x] T011 [P] [US2] Write test that `save_annotations`
  accepts `file_path` parameter and writes correct markdown
  files from a JSON file in tests/test_mcp_server.py
- [x] T012 [P] [US2] Write test that `save_annotations` with
  inline `annotations` parameter still works (backward compat)
  in tests/test_mcp_server.py
- [x] T013 [P] [US2] Write test that `save_annotations` raises
  `ValueError` when both `file_path` and `annotations` are
  provided in tests/test_mcp_server.py
- [x] T014 [P] [US2] Write test that `save_annotations` raises
  `ValueError` when neither `file_path` nor `annotations` is
  provided in tests/test_mcp_server.py
- [x] T015 [P] [US2] Write test that `save_annotations` raises
  `FileNotFoundError` when `file_path` does not exist in
  tests/test_mcp_server.py

### Implementation for User Story 2

- [x] T016 [US2] Refactor `save_annotations` in
  src/otb/mcp_server.py to accept optional `file_path: str |
  None = None` and make `annotations` optional (`list[dict[str,
  Any]] | None = None`). Add validation: raise `ValueError` if
  both or neither provided. When `file_path` given, read JSON
  and convert to annotation list.
- [x] T017 [US2] Update existing `save_annotations` tests in
  tests/test_mcp_server.py that call with positional args to
  use keyword `annotations=` explicitly
- [x] T018 [US2] Run `uv run pytest tests/test_mcp_server.py`
  and verify all US1 + US2 tests pass
- [x] T019 [US2] Run `uv run mypy src/otb/mcp_server.py` and
  `uv run pylint src/otb/mcp_server.py` — fix any issues

**Checkpoint**: `save_annotations` works with both `file_path`
and `annotations` parameters. Mutual exclusion enforced. All
tests green.

---

## Phase 5: User Story 3 - End-to-End Prompt (Priority: P3)

**Goal**: Update `kindle_import_annotations` MCP prompt to
orchestrate the file-path-based workflow with ~30-annotation
batch guidance.

**Independent Test**: Call `kindle_import_annotations` and
verify the returned prompt text references file-path-based
tool calls and batch size of ~30.

### Tests for User Story 3

> **Write these tests FIRST, ensure they FAIL before
> implementation**

- [x] T020 [P] [US3] Write test that
  `kindle_import_annotations` prompt text references
  `file_path` parameter (not inline annotations array) in
  tests/test_mcp_server.py
- [x] T021 [P] [US3] Write test that prompt text contains
  batch size guidance (~30 annotations) in
  tests/test_mcp_server.py

### Implementation for User Story 3

- [x] T022 [US3] Update `kindle_import_annotations` prompt in
  src/otb/mcp_server.py to describe the file-path workflow:
  Step 1 returns summary with `file_path`; Step 2 reads temp
  file in batches of ~30 for title generation; Step 3 calls
  `save_annotations(file_path=..., directory=...)`. Remove
  fallback title instruction (annotations saved without title
  on failure per clarification).
- [x] T023 [US3] Update existing prompt tests in
  tests/test_mcp_server.py
  (`test_kindle_import_contains_tool_names`,
  `test_kindle_import_contains_title_instructions`) to match
  the new prompt content
- [x] T024 [US3] Update the MCP server module docstring at top
  of src/otb/mcp_server.py and the `mcp` FastMCP instructions
  string to reflect the file-path workflow
- [x] T025 [US3] Run `uv run pytest tests/test_mcp_server.py`
  and verify all tests pass

**Checkpoint**: Full workflow orchestrated via file-path-based
prompt. All tests green.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T026 Run full test suite: `uv run pytest`
- [x] T027 [P] Run type checker: `uv run mypy src/ tests/`
- [x] T028 [P] Run linter: `uv run pylint src/ tests/`
- [x] T029 Run markdown linter:
  `pymarkdownlnt scan -r --respect-gitignore .`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: N/A (empty)
- **US1 (Phase 3)**: Can start immediately after Setup
- **US2 (Phase 4)**: Can start after Setup (independent of
  US1 — uses its own temp JSON fixtures)
- **US3 (Phase 5)**: Depends on US1 and US2 completion
  (prompt references both tool changes)
- **Polish (Phase 6)**: After all user stories complete

### User Story Dependencies

- **US1 (P1)**: Independent — no deps on other stories
- **US2 (P2)**: Independent — no deps on other stories
- **US3 (P3)**: Depends on US1 + US2 (prompt references both
  refactored tools)

### Within Each User Story

- Tests written and confirmed FAILING before implementation
- Implementation tasks in dependency order
- Quality gates (mypy, pylint) at end of each story

### Parallel Opportunities

- T002-T006 (US1 tests) can all run in parallel
- T011-T015 (US2 tests) can all run in parallel
- T020-T021 (US3 tests) can run in parallel
- US1 and US2 can be implemented in parallel (different
  tool functions, independent test fixtures)
- T027 and T028 can run in parallel

---

## Parallel Example: User Story 1

```text
# Write all US1 tests in parallel:
T002: test parse returns dict with summary keys
T003: test temp file contains valid JSON annotations
T004: test count matches annotation count
T005: test chapters list
T006: test FileNotFoundError still works
```

## Parallel Example: User Story 2

```text
# Write all US2 tests in parallel:
T011: test file_path parameter writes files
T012: test backward compat with annotations param
T013: test ValueError on both params
T014: test ValueError on neither param
T015: test FileNotFoundError on bad file_path
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 3: US1 (T002-T010)
3. **STOP and VALIDATE**: `parse_kindle_export` returns
   summary, temp file written correctly
4. This alone solves the 113K token explosion

### Incremental Delivery

1. US1 → Parse tool writes temp file (solves token overflow)
2. US2 → Save tool reads from file (solves batched saves)
3. US3 → Prompt updated (complete workflow integration)
4. Each story adds value without breaking previous stories

---

## Notes

- All changes are in 2 files: `src/otb/mcp_server.py` and
  `tests/test_mcp_server.py`
- No new dependencies — uses stdlib `json` and `tempfile`
- Existing tests must be updated (return type changes)
- Constitution III (Test-First) strictly enforced

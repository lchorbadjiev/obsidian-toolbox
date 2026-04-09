# Tasks: Boox Import Annotations Prompt

**Input**: Design documents from `/specs/012-boox-import-prompt/`
**Prerequisites**: plan.md, spec.md, research.md, contracts/

**Organization**: Single user story — one MCP prompt function.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Phase 1: User Story 1 & 2 — Boox Import Prompt (Priority: P1)

**Goal**: Register a `boox_import_annotations` MCP prompt that
returns step-by-step instructions for the full Boox import
workflow (parse, title generation, save).

**Independent Test**: Call the prompt with a directory path and
verify the returned message references `parse_boox_export` and
`save_annotations`.

### Tests for User Story 1 & 2

> **NOTE: Write these tests FIRST, ensure they FAIL before
> implementation (Constitution III)**

- [x] T001 [P] [US1] Write test
  `test_boox_import_returns_messages` in
  `tests/test_mcp_server.py` verifying that
  `boox_import_annotations(directory_path=...)` returns a
  non-empty list of messages
- [x] T002 [P] [US1] Write test
  `test_boox_import_contains_tool_names` in
  `tests/test_mcp_server.py` verifying the message content
  contains `parse_boox_export` and `save_annotations`
- [x] T003 [P] [US1] Write test
  `test_boox_import_derives_notes_directory` in
  `tests/test_mcp_server.py` verifying the output directory
  is derived as `{input}/notes/`
- [x] T004 [P] [US2] Write test
  `test_boox_import_contains_title_instructions` in
  `tests/test_mcp_server.py` verifying the message mentions
  title generation in batches using a lightweight model
- [x] T005 [P] [US1] Write test
  `test_boox_import_mentions_figures` in
  `tests/test_mcp_server.py` verifying the message mentions
  figure extraction when EPUB is present

### Implementation for User Story 1 & 2

- [x] T006 [US1] Add `boox_import_annotations` function
  decorated with `@mcp.prompt` in `src/otb/mcp_server.py`
  accepting `directory_path: str` parameter, returning
  `list[UserMessage]` with step-by-step instructions
  mirroring the `kindle_import_annotations` pattern.
  Steps: (1) call `parse_boox_export`, (2) generate titles
  in batches of ~30 with lightweight model, (3) call
  `save_annotations`. Derive output dir as
  `{directory_path}/notes/`. Mention EPUB figure extraction.
- [x] T007 [US1] Run `uv run pytest tests/test_mcp_server.py
  -k boox_import` and verify all tests pass (green)
- [x] T008 [US1] Run `uv run mypy src/otb/mcp_server.py` and
  `uv run pylint src/otb/mcp_server.py` — fix any issues

**Checkpoint**: Prompt registered and tested

---

## Phase 2: Polish & Cross-Cutting Concerns

**Purpose**: Final validation

- [x] T009 Run `uv run pytest` — verify all tests pass
- [x] T010 Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — verify 10/10
- [x] T011 Run `pymarkdownlnt scan -r --respect-gitignore .`
  — fix any markdown lint issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **US1+US2 (Phase 1)**: No dependencies — start immediately
- **Polish (Phase 2)**: Depends on Phase 1

### Parallel Opportunities

- T001-T005: All test-writing tasks in parallel (same file
  but independent test functions)

---

## Implementation Strategy

### MVP

1. Write tests T001-T005 (all pass as red)
2. Implement prompt T006
3. Verify green T007-T008
4. Polish T009-T011

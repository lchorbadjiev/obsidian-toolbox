# Tasks: Kindle Import Annotations Prompt

**Input**: Design documents from
`/specs/008-kindle-import-prompt/`
**Prerequisites**: plan.md, spec.md, research.md,
data-model.md, contracts/

**Tests**: Required (Constitution Principle III:
Test-First).

**Organization**: Tasks grouped by user story.

## Format: `[ID] [P?] [Story] Description`

+ **[P]**: Can run in parallel (different files, no
  dependencies)
+ **[Story]**: Which user story this task belongs to
  (US1, US2)
+ Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No new files needed. The prompt function
goes in the existing `src/otb/mcp_server.py`.

No setup tasks required.

---

## Phase 2: User Story 1 — Import Prompt (P1) MVP

**Goal**: Add the `kindle-import-annotations` MCP prompt
that returns orchestration instructions.

**Independent Test**: Call the prompt function with a
file path and directory, verify it returns a message
list with the correct tool call instructions.

### Tests for User Story 1

> **Write these tests FIRST, ensure they FAIL before
> implementation.**

+ [X] T001 [P] [US1] Write failing test for prompt
  return type in `tests/test_mcp_server.py`: call
  `kindle_import_annotations(file_path="/tmp/test.html",
  directory="/tmp/out")`, assert it returns a list with
  at least one message with role "user"
+ [X] T002 [P] [US1] Write failing test for prompt
  content in `tests/test_mcp_server.py`: assert the
  message text contains `parse_kindle_export`,
  `save_annotations`, the file_path value, and the
  directory value
+ [X] T003 [P] [US1] Write failing test for title
  generation instructions in `tests/test_mcp_server.py`:
  assert the message text contains instructions to
  generate a title for each annotation (e.g., "title"
  and "under 10 words")

### Implementation for User Story 1

+ [X] T004 [US1] Implement `kindle_import_annotations`
  prompt in `src/otb/mcp_server.py`: add
  `@mcp.prompt()` decorator on function
  `kindle_import_annotations(file_path: str,
  directory: str) -> list[UserMessage]` that returns
  step-by-step instructions for the MCP client to
  parse, generate titles, and save annotations
+ [X] T005 [US1] Verify all US1 tests pass:
  `uv run pytest tests/test_mcp_server.py -k "kindle_import"`

**Checkpoint**: Prompt works and returns correct
orchestration instructions.

---

## Phase 3: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates and final validation.

+ [X] T006 [P] Run full test suite: `uv run pytest`
+ [X] T007 [P] Run type checker:
  `uv run mypy src/ tests/`
+ [X] T008 [P] Run linter: `uv run pylint src/ tests/`
+ [X] T009 [P] Run markdown linter:
  `pymarkdownlnt scan -r --respect-gitignore .`
+ [X] T010 Run quickstart.md validation: verify the
  prompt is listed when starting the MCP server

---

## Dependencies & Execution Order

### Phase Dependencies

+ **US1 (Phase 2)**: No dependencies — uses existing
  tools
+ **Polish (Phase 3)**: Depends on Phase 2

### Within User Story 1

+ Tests MUST be written and FAIL before implementation
+ T001-T003 (tests) can be written in parallel
+ T004 (implementation) depends on tests existing
+ T005 (verification) depends on T004

### Parallel Opportunities

+ T001-T003 (all US1 tests) can be written in parallel
+ T006-T009 (quality gates) can all run in parallel

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Write tests (T001-T003)
2. Implement prompt (T004)
3. Verify (T005)
4. Quality gates (T006-T010)

This is a single-story feature. US2 (error reporting)
is handled by the existing tools — the prompt just
returns instructions; errors surface when the MCP
client executes the tool calls.

---

## Notes

+ [P] tasks = different files, no dependencies
+ [Story] label maps task to specific user story
+ Constitution Principle III requires test-first
+ This is a small feature: one function + tests

---
description: "Task list for Kindle MCP Server"
---

# Tasks: Kindle MCP Server

**Input**: Design documents from `/specs/001-kindle-mcp-server/`
**Prerequisites**: plan.md, spec.md

**Organization**: Tasks are grouped by user story to enable independent implementation
and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Add new runtime dependency.

- [ ] T001 Add `mcp` to `[project].dependencies` in `pyproject.toml` and run `uv sync`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Parser and markdown-parser changes that both user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T002 Add `generate_title: bool = True` parameter to `_parse_highlight` and `parse_notebook` in `src/otb/parser.py`; when `False`, leave `Highlight.title` as `""`  (existing callers are unaffected — default preserves current behaviour)
- [ ] T003 [P] Update `parse_highlight_md` in `src/otb/md_parser.py` to make the `# heading` optional — return `title=""` instead of raising `ValueError` when no H1 is found (required for round-trip compliance with title-less files)
- [ ] T004 [P] Add test to `tests/test_parser.py` verifying `parse_notebook(path, generate_title=False)` returns highlights with `title == ""` using the existing HTML fixture at `tests/fixtures/`

**Checkpoint**: Foundation ready — both user story phases can now begin.

---

## Phase 3: User Story 1 - Parse Kindle Export into Highlights (Priority: P1) 🎯 MVP

**Goal**: LLM agent calls one MCP tool, receives a list of raw highlights with no titles.

**Independent Test**: Call `parse_kindle_export` with the existing HTML fixture path;
verify a non-empty list is returned, each item has `book`, `chapter`, `page`,
`location`, `text`, and `color`, and that `title` is absent or empty on every item.

- [ ] T005 [P] [US1] Write failing tests in `tests/test_mcp_server.py` for the `parse_kindle_export` tool handler function: (a) valid HTML fixture path → list of highlights with empty titles; (b) non-existent path → raises / returns error; (c) empty export → returns empty list
- [ ] T006 [US1] Create `src/otb/mcp_server.py` with a FastMCP server instance and `parse_kindle_export` tool that delegates to `parse_notebook(path, generate_title=False)`; tool description MUST instruct the host LLM to generate a concise title for each highlight before calling the save tool
- [ ] T007 [US1] Add `otb mcp` command to `src/otb/cli.py` under the top-level `main` group; the command MUST start the MCP server with stdio transport by calling `mcp_server.run()`

**Checkpoint**: US1 complete — `otb mcp` starts, `parse_kindle_export` tool works end-to-end.

---

## Phase 4: User Story 2 - Save Highlights as Markdown Files (Priority: P2)

**Goal**: LLM agent calls one MCP tool with a list of highlights and a directory path;
one markdown file per highlight is written in the correct format.

**Independent Test**: Call `save_highlights` with the fixtures from US1 (plus
LLM-assigned titles) and a temp directory; verify one `.md` file per highlight exists,
frontmatter fields match, and each file can be re-parsed by `parse_highlight_md`
without error.

- [ ] T008 [P] [US2] Write failing tests in `tests/test_md_writer.py` covering: (a) highlight with title → correct filename `{number:03d} - {sanitized_title}.md` and frontmatter; (b) highlight without title → filename `{number:03d}.md`, no H1 line written; (c) non-existent directory → created automatically; (d) two highlights with identical text → unique filenames via number prefix; (e) round-trip: written file parsed back by `parse_highlight_md` returns equivalent `Highlight`
- [ ] T009 [P] [US2] Write failing tests in `tests/test_mcp_server.py` for the `save_highlights` tool handler function: (a) valid highlights + writable dir → returns list of created file paths; (b) non-writable dir → returns descriptive error, no partial files
- [ ] T010 [US2] Create `src/otb/md_writer.py` with: `write_highlight(h: Highlight, directory: Path) -> Path` (writes one file, creates dir if needed) and `write_highlights(highlights: list[Highlight], directory: Path) -> list[Path]` (writes all, aborts on first error); filename format: `f"{h.number:03d} - {sanitize(h.title)}.md"` when title present, `f"{h.number:03d}.md"` otherwise; frontmatter fields: `source`, `author`, `chapter`, `page`, `location`, `type: highlight`, `number`; body: optional `# {title}` then `> {text}`
- [ ] T011 [US2] Add `save_highlights` tool to `src/otb/mcp_server.py` that accepts a list of highlight dicts and a `directory` string, deserialises into `Highlight` objects, delegates to `write_highlights`, and returns the list of written paths

**Checkpoint**: US2 complete — full parse → title → save workflow works end-to-end.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Quality gates and final validation.

- [ ] T012 [P] Run `uv run mypy src/ tests/` and fix all type errors in `src/otb/parser.py`, `src/otb/md_parser.py`, `src/otb/md_writer.py`, `src/otb/mcp_server.py`, `src/otb/cli.py`, and new test files
- [ ] T013 [P] Run `uv run pylint src/ tests/` and fix all issues to reach 10/10; add file-level `missing-function-docstring` disable comment to new test files only; justify any new suppressions with inline comments
- [ ] T014 Run `uv run pytest` and verify all tests (existing + new) pass with no failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (uv sync must complete first)
- **User Stories (Phase 3, 4)**: Both depend on Phase 2 completion; can then run in parallel
- **Polish (Phase 5)**: Depends on all implementation tasks being complete

### User Story Dependencies

- **US1 (Phase 3)**: No dependency on US2 — independently testable after Phase 2
- **US2 (Phase 4)**: No dependency on US1 — independently testable after Phase 2 (uses same parser output as input, but does not require the MCP parse tool to be complete)

### Within Each User Story

- Tests (T005, T008, T009) MUST be written and confirmed to FAIL before implementation
- T006 must precede T007 (CLI command requires server to exist)
- T010 must precede T011 (save tool requires writer to exist)

### Parallel Opportunities

```bash
# Phase 2 — run together after T001:
T003  # md_parser.py H1-optional change
T004  # test_parser.py generate_title=False test

# Phase 3 + Phase 4 — start both after Phase 2 checkpoint:
T005  # test_mcp_server.py parse tool tests
T008  # test_md_writer.py writer tests
T009  # test_mcp_server.py save tool tests

# Phase 5 — run together after T014 deps:
T012  # mypy
T013  # pylint
```

---

## Implementation Strategy

### MVP (User Story 1 only)

1. T001 → T002 → T004 (foundation)
2. T005 → T006 → T007 (parse tool + CLI)
3. **STOP**: verify `otb mcp` starts and `parse_kindle_export` returns highlights
4. Demonstrate to user with a real Kindle export file

### Incremental Delivery

1. Phase 1 + 2 → foundation ready
2. Phase 3 → `parse_kindle_export` works → demo MVP
3. Phase 4 → `save_highlights` works → full workflow demo
4. Phase 5 → quality gates pass → ready to merge

---

## Notes

- `[P]` tasks touch different files and have no inter-dependencies — safe to run in parallel
- Tests MUST fail before implementation (Constitution Principle III — NON-NEGOTIABLE)
- `generate_title=True` default in `parse_notebook` preserves all existing CLI behaviour
- `md_writer.py` filename sanitisation: strip characters invalid in filenames; keep it simple (replace `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `-`; truncate to 60 chars)
- The `save_highlights` MCP tool receives highlight data as JSON-serialisable dicts over the MCP protocol; deserialisation into `Highlight` dataclasses happens inside the tool handler

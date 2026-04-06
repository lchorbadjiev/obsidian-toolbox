# Tasks: Parse MD Highlights MCP Tool

**Input**: Design documents from `/specs/002-parse-md-highlights/`
**Prerequisites**: plan.md, spec.md

**Note**: No setup or foundational phases required — no new dependencies, no schema
changes, no shared infrastructure. All work is additions to existing files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Paths are relative to repository root

---

## Phase 2: User Story 1 - Read a Highlights Directory via MCP (Priority: P1) 🎯 MVP

**Goal**: LLM agent calls `parse_md_highlights_dir` with a directory path and receives
a sorted list of highlights from all `.md` files; malformed files are reported without
aborting the call. `otb md count` provides the same capability from the CLI.

**Independent Test**: Call `parse_md_highlights_dir` with `tests/fixtures/highlights/`;
verify 4 highlights returned in filename order, each with correct fields. Call
`otb md count tests/fixtures/highlights/` and verify it prints `4`.

- [x] T001 [P] [US1] Write failing tests in
  `tests/test_mcp_server.py` for
  `parse_md_highlights_dir`: (a) valid fixtures dir
  → 4 highlights in filename order with correct
  fields; (b) non-existent path → error; (c) path is
  a file not a dir → error; (d) empty directory →
  empty highlights list; (e) directory with one
  malformed `.md` file → good highlights returned +
  parse_errors dict populated for the bad file
- [x] T002 [P] [US1] Write failing tests in
  `tests/test_cli_md.py` for `otb md count`:
  (a) valid dir → prints count to stdout;
  (b) non-existent path → non-zero exit;
  (c) empty dir → prints `0`
- [x] T003 [US1] Add `parse_md_highlights_dir` tool
  to `src/otb/mcp_server.py`: accepts
  `directory: str`; iterates sorted `.md` files in
  that directory (non-recursive); calls
  `parse_highlight_md` per file in try/except;
  returns
  `{"highlights": [...], "parse_errors": {...}}`;
  raises `NotADirectoryError` if path is a file,
  `FileNotFoundError` if path does not exist
- [x] T004 [US1] Add `otb md` Click group and
  `otb md count` command to `src/otb/cli.py`;
  `count` accepts a `PATH` argument
  (`click.Path(exists=True, file_okay=False,
  path_type=Path)`) and prints the number of
  successfully parsed highlights via
  `parse_highlight_dir`

**Checkpoint**: US1 complete — both
`parse_md_highlights_dir` MCP tool and
`otb md count` CLI command work end-to-end.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [x] T005 [P] Run `uv run mypy src/ tests/` and
  fix all type errors in modified files
  (`src/otb/mcp_server.py`, `src/otb/cli.py`) and
  new test files
- [x] T006 [P] Run `uv run pylint src/ tests/` and
  fix all issues to reach 10/10; add file-level
  `missing-function-docstring` disable to
  `tests/test_cli_md.py`
- [x] T007 Run `uv run pytest` and verify all 41 existing tests plus new tests pass

---

## Dependencies & Execution Order

- T001 and T002 are independent (different files) — run in parallel
- T003 depends on T001 reaching a green state (write test → confirm fail → implement)
- T004 depends on T002 reaching a green state
- T003 and T004 are independent of each other — run in parallel once tests are written
- T005 and T006 are independent — run in parallel after T003 and T004
- T007 runs last

### Parallel Opportunities

```bash
# Write both test files together:
T001  # tests/test_mcp_server.py additions
T002  # tests/test_cli_md.py new file

# Implement both after tests confirmed failing:
T003  # mcp_server.py new tool
T004  # cli.py new group + command

# Quality gates together:
T005  # mypy
T006  # pylint
```

---

## Notes

- `[P]` tasks touch different files — safe to run in parallel
- Tests MUST fail before implementation (Constitution Principle III)
- `parse_md_highlights_dir` iterates files itself
  rather than calling `parse_highlight_dir` so it can
  catch per-file errors without changing
  `md_parser.py`
- `otb md count` uses the existing
  `parse_highlight_dir` (fail-fast is acceptable for
  CLI)
- `tests/test_cli_md.py` is a new test file; use
  Click's `CliRunner` for command testing

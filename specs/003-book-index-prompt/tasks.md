---
description: "Task list for Book Index Generation Prompt"
---

# Tasks: Book Index Generation Prompt

**Input**: Design documents from `/specs/003-book-index-prompt/`
**Prerequisites**: plan.md, spec.md, research.md

**Note**: No setup or foundational phases required — no new files,
no new dependencies, no new infrastructure. All work is additions
to existing files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Paths are relative to repository root

---

## Phase 2: User Story 1 - Generate Book Index via MCP Prompt
## (Priority: P1) 🎯 MVP

**Goal**: LLM agent calls `generate_book_index` with a highlights
directory and receives a `UserMessage` containing all highlight data
plus instructions to generate a book index markdown file.
`otb md index-prompt` provides the same capability from the CLI.

**Independent Test**: Call `generate_book_index` with
`tests/fixtures/highlights/`; verify it returns a list containing
one `UserMessage` whose text includes the book title, author, and
highlight entries grouped by chapter. Call
`otb md index-prompt tests/fixtures/highlights/` and verify it prints
the prompt text to stdout with exit code 0.

- [x] T001 [P] [US1] Write failing tests in `tests/test_mcp_server.py`
  for `generate_book_index`: (a) valid fixtures dir → returns
  `list[Message]` with one `UserMessage` containing book title,
  author, highlight text, and chapter groupings; (b) wikilink entries
  follow `[[notes/NNN - Title]]` format; (c) non-existent path →
  returns list with error `UserMessage` (no exception raised); (d)
  path is a file not a dir → returns list with error `UserMessage`;
  (e) empty directory → returns list with informative `UserMessage`;
  (f) directory with one malformed `.md` file → valid highlights
  still present in message, skipped file mentioned
- [x] T002 [P] [US1] Write failing tests in `tests/test_cli_md.py`
  for `otb md index-prompt`: (a) valid dir → exit 0, stdout contains
  book title and highlight data; (b) non-existent path → non-zero
  exit (Click `exists=True` validation)
- [x] T003 [US1] Add `_build_index_prompt(directory: str) -> str`
  helper and `generate_book_index` MCP prompt to
  `src/otb/mcp_server.py`: helper iterates sorted `*.md` files in
  per-file try/except using `parse_highlight_md`, groups highlights
  by chapter, returns formatted string with book metadata +
  chapter-grouped highlight list (number, title, text) + wikilink
  entries (`[[notes/NNN - Title]]`) + LLM instructions for
  frontmatter, prose summary, and "Notes by Chapter" section; on bad
  path or empty dir returns descriptive string instead of raising;
  prompt function returns `[UserMessage(content=prompt_text)]` using
  `from mcp.server.fastmcp.prompts.base import UserMessage`
- [x] T004 [US1] Add `otb md index-prompt` command to
  `src/otb/cli.py`: accepts a `PATH` argument
  (`click.Path(exists=True, file_okay=False, path_type=Path)`) and
  prints `_build_index_prompt(str(path))` to stdout; import
  `_build_index_prompt` from `otb.mcp_server`

**Checkpoint**: US1 complete — both `generate_book_index` MCP prompt
and `otb md index-prompt` CLI command work end-to-end.

---

## Phase 3: Polish & Cross-Cutting Concerns

- [x] T005 [P] Run `uv run mypy src/ tests/` and fix all type errors
  in modified files (`src/otb/mcp_server.py`, `src/otb/cli.py`) and
  updated test files
- [x] T006 [P] Run `uv run pylint src/ tests/` and fix all issues to
  reach 10/10; add `UserMessage` import to existing pylint disable
  comment if needed
- [x] T007 Run `uv run pytest` and verify all existing tests plus new
  tests pass

---

## Dependencies & Execution Order

- T001 and T002 are independent (different files) — run in parallel
- T003 depends on T001 reaching a confirmed-failing state
- T004 depends on T002 reaching a confirmed-failing state
- T003 and T004 are independent of each other — run in parallel once
  tests are written
- T005 and T006 are independent — run in parallel after T003 and T004
- T007 runs last

### Parallel Opportunities

```bash
# Write both test files together:
T001  # tests/test_mcp_server.py additions
T002  # tests/test_cli_md.py additions

# Implement both after tests confirmed failing:
T003  # mcp_server.py prompt + helper
T004  # cli.py new command

# Quality gates together:
T005  # mypy
T006  # pylint
```

---

## Notes

- `[P]` tasks touch different files — safe to run in parallel
- Tests MUST fail before implementation (Constitution Principle III)
- `_build_index_prompt` is the shared helper called by both the MCP
  prompt and the CLI command — no logic duplication (Principle VI)
- Error cases return a descriptive `UserMessage`; they do NOT raise
  exceptions, because prompts must always return messages
- The `UserMessage` type is from
  `mcp.server.fastmcp.prompts.base`; it is part of the existing
  `mcp` package — no new dependency required (Principle V)
- Prose lines in all docs MUST wrap at 80 characters
  (Constitution Principle VII)

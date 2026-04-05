# Implementation Plan: Book Index Generation Prompt

**Branch**: `003-book-index-prompt` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-book-index-prompt/spec.md`

## Summary

Add a `generate_book_index` MCP prompt to `mcp_server.py` that reads a directory of highlight
markdown files, groups them by chapter, and returns a `UserMessage` containing all highlight
data plus instructions for the host LLM to generate a book index markdown file. The index
format (frontmatter, prose summary, "Notes by Chapter" with wikilinks) matches the example in
`tmp/The Invention of Science - Index.md`. A matching `otb md index-prompt <directory>` CLI
command prints the prompt text to stdout (Constitution Principle I). No new dependencies.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: `mcp` (FastMCP) — already installed; `click` — already installed  
**Storage**: N/A (read-only; no files written)  
**Testing**: pytest, Click CliRunner  
**Target Platform**: macOS / Linux (same as existing project)  
**Project Type**: CLI tool + MCP server (existing project, additions only)  
**Performance Goals**: N/A (small local directories, interactive use)  
**Constraints**: Zero new package dependencies  
**Scale/Scope**: Single-user local tool; directories up to ~200 highlight files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | ✓ PASS | `otb md index-prompt <directory>` added to `src/otb/cli.py` |
| II. Shared Parser Contract | ✓ PASS | Uses existing `parse_highlight_md`; no new parser |
| III. Test-First | ✓ PASS | Tests written and confirmed failing before implementation |
| IV. Type Safety & Lint | ✓ PASS | mypy zero-error + pylint 10/10 enforced |
| V. Simplicity | ✓ PASS | Zero new dependencies; `Message`/`UserMessage` from existing `mcp` package |
| VI. MCP Server | ✓ PASS | `@mcp.prompt()` primitive registered; CLI backed by same helper function |

**Note on Principle VI**: The constitution states "every user-facing CLI capability MUST also
be registered as an MCP tool." This feature introduces an MCP *prompt* (not a tool), with the
CLI as its counterpart. The MCP prompt IS the primary MCP registration; the CLI calls the same
underlying helper. No separate MCP tool is needed because the prompt already exposes the
capability to agents.

## Project Structure

### Documentation (this feature)

```text
specs/003-book-index-prompt/
├── plan.md          # This file
├── research.md      # Phase 0 output
├── spec.md          # Feature specification
├── checklists/
│   └── requirements.md
└── tasks.md         # Phase 2 output (/speckit.tasks)
```

### Source Code (modified files only)

```text
src/otb/
├── mcp_server.py    # Add generate_book_index prompt + _build_index_prompt helper
└── cli.py           # Add otb md index-prompt command

tests/
├── test_mcp_server.py   # Add prompt tests
└── test_cli_md.py       # Add index-prompt CLI tests
```

No new files required. All additions are to existing files.

### Key Implementation Details

**`_build_index_prompt(directory: str) -> str`** (private helper in `mcp_server.py`):
- Reads `*.md` files from `directory` sorted by filename
- Per-file try/except using `parse_highlight_md`; collects valid highlights + error filenames
- Groups highlights by `chapter` field, preserving filename-sorted order within each group
- Builds and returns a formatted string containing:
  1. Book metadata (title, author from first valid highlight)
  2. Highlights grouped by chapter (number, title, text per highlight)
  3. Wikilink template: `[[notes/NNN - Title]]` derived from highlight number + title
  4. Instructions for the LLM to generate frontmatter, prose summary, and "Notes by Chapter"
- On bad path: returns an error string (not raised — callers handle it as a message)
- On empty directory: returns an informative string

**`generate_book_index(directory: str) -> list[Message]`** (MCP prompt in `mcp_server.py`):
- Calls `_build_index_prompt(directory)`
- Returns `[UserMessage(content=prompt_text)]`
- Import: `from mcp.server.fastmcp.prompts.base import Message, UserMessage`

**`otb md index-prompt <directory>`** (CLI command in `cli.py`):
- `click.Path(exists=True, file_okay=False, path_type=Path)` argument
- Calls `_build_index_prompt(str(path))` and prints result to stdout
- Errors (invalid path) handled by Click's `exists=True` constraint

### Prompt Text Structure

```
You are given highlights from "{book_title}" by {author}.

Generate a book index markdown file in this exact format:

---
tags: [book]
author: {author}
published: {year_or_blank}
---

# {full_book_title}

{prose summary of the book's argument, themes, and significance — 2-4 paragraphs}

---

## Notes by Chapter

### {chapter_name}
- [[notes/{NNN} - {title}]]
...

### {next_chapter_name}
...

---

Highlights by chapter:

## {chapter_name}

{number:03d} - {title}
> {text}

...
```

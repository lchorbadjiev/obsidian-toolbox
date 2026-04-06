# Implementation Plan: Parse Zotero Annotations

**Branch**: `006-parse-zotero-annotations` | **Date**: 2026-04-06
| **Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/006-parse-zotero-annotations/spec.md`

Prose lines MUST wrap at 80 characters (Constitution
Principle VII).

## Summary

Add a Zotero annotation parser (`zotero_parser.py`) that reads
Zotero's markdown annotation export and companion `book.txt`
metadata file, producing `list[Annotation]` using the shared
dataclass. Wire it to a new `otb zotero parse` CLI command that
delegates to the existing `md_writer.py` for output, and expose
it as an MCP tool. No new dependencies.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: click, mcp (FastMCP) -- already
installed; no new deps
**Storage**: Filesystem (reads Zotero exports, writes markdown
files via existing `md_writer.py`)
**Testing**: pytest with fixtures in `tests/fixtures/zotero/`
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI tool + MCP server
**Performance Goals**: N/A (batch tool, small input files)
**Constraints**: No new dependencies (Constitution Principle V)
**Scale/Scope**: Single book export at a time; hundreds of
annotations per file at most

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | PASS | `otb zotero parse` command planned |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Fixtures exist; tests planned first |
| IV. Type Safety & Lint | PASS | mypy + pylint targets maintained |
| V. Simplicity | PASS | Regex parser, no new deps |
| VI. MCP Server | PASS | `parse_zotero_export` tool planned |
| VII. Document Formatting | PASS | 80-char wrapping enforced |

No violations. Complexity Tracking table not needed.

## Project Structure

### Documentation (this feature)

```text
specs/006-parse-zotero-annotations/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── mcp.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/otb/
├── zotero_parser.py   # NEW: parse Zotero exports
├── cli.py             # MODIFIED: add zotero group + parse cmd
├── mcp_server.py      # MODIFIED: add parse_zotero_export tool
├── parser.py          # UNCHANGED: shared dataclasses
├── md_parser.py       # UNCHANGED
└── md_writer.py       # UNCHANGED: reused for output

tests/
├── test_zotero_parser.py  # NEW: parser unit tests
├── test_cli_zotero.py     # NEW: CLI integration tests
└── fixtures/zotero/       # EXISTING
    ├── Annotations.md
    └── book.txt
```

**Structure Decision**: Single new module (`zotero_parser.py`)
following the same pattern as `parser.py` and `md_parser.py`.
CLI and MCP modifications are minimal additions to existing
files. Writer is reused without changes.

## Implementation Phases

### Phase 1: Zotero Parser Module (test-first)

1. Create `tests/test_zotero_parser.py` with failing tests:
   - Test `parse_book_metadata()` extracts title and author
     from `book.txt` fixture.
   - Test `parse_zotero_annotations()` returns correct count
     of annotations from `Annotations.md` fixture.
   - Test annotation fields: `page`, `location` (= page),
     `text`, `title`, `number`, `chapter` (empty), `color`
     (None).
   - Test edge cases: short fragments, single-word annotations.
   - Test error: missing `book.txt` raises `FileNotFoundError`.
   - Test: empty `Annotations.md` returns empty list.

2. Create `src/otb/zotero_parser.py`:
   - `parse_book_metadata(path: Path) -> Book` -- reads
     `book.txt`, extracts Title and Authors fields.
   - `parse_zotero_annotations(directory: Path) -> list[Annotation]`
     -- reads both files, parses each annotation line with
     regex, assigns sequential numbers, generates titles.
   - Regex pattern for annotation lines:
     `"(.+?)"\s+\(".*?",\s*p\.\s*(\w+)\)`
   - Reuse `_title_from_text()` from `parser.py` (may need
     to make it importable or duplicate the small function).

3. Verify: `uv run pytest tests/test_zotero_parser.py` green.

### Phase 2: CLI Command

1. Add failing test in `tests/test_cli_zotero.py`:
   - Test `otb zotero parse <input> <output>` writes correct
     number of files.
   - Test output files are parseable by `md_parser.py`
     (round-trip).
   - Test missing input files produce exit code 1.

2. Add to `src/otb/cli.py`:
   - `@main.group() def zotero()` -- command group.
   - `@zotero.command("parse")` -- parse subcommand with
     `INPUT_DIR` and `OUTPUT_DIR` arguments.
   - Delegates to `parse_zotero_annotations()` then
     `write_annotations()`.

3. Verify: `uv run pytest tests/test_cli_zotero.py` green.

### Phase 3: MCP Tool

1. Add failing test in `tests/test_mcp_server.py` (append):
   - Test `parse_zotero_export` tool returns correct annotation
     dicts.
   - Test error handling for missing directory.

2. Add to `src/otb/mcp_server.py`:
   - `@mcp.tool()` decorator on `parse_zotero_export(path: str)`
   - Delegates to `parse_zotero_annotations()`, converts to
     dicts using existing `_annotation_to_dict()`.

3. Verify: `uv run pytest tests/test_mcp_server.py` green.

### Phase 4: Quality Gates

1. `uv run pytest` -- all tests pass.
2. `uv run mypy src/ tests/` -- zero errors.
3. `uv run pylint src/ tests/` -- 10/10.
4. `npx markdownlint-cli "**/*.md"` -- zero errors.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | PASS | `otb zotero parse` implemented |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Tests written before implementation |
| IV. Type Safety & Lint | PASS | mypy + pylint clean |
| V. Simplicity | PASS | Regex only, no new deps |
| VI. MCP Server | PASS | `parse_zotero_export` tool added |
| VII. Document Formatting | PASS | 80-char prose, markdownlint clean |

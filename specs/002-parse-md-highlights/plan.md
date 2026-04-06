# Implementation Plan: Parse MD Highlights MCP Tool

**Branch**: `002-parse-md-highlights` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-parse-md-highlights/spec.md`

## Summary

Add a `parse_md_highlights_dir` MCP tool to the existing server that accepts a
directory path and returns all highlights found in `.md` files, sorted by filename.
Malformed files are skipped with per-file error reporting rather than aborting the
whole call. Also adds an `otb md count` CLI command (required by Constitution
Principle I). No new dependencies needed — delegates entirely to the existing
`parse_highlight_md` function in `md_parser.py`.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: all existing (`click`, `beautifulsoup4`,
`mcp`) — no new deps
**Storage**: N/A (read-only; no files written)
**Testing**: pytest; tests use existing markdown fixtures in `tests/fixtures/highlights/`
**Target Platform**: macOS / Linux (personal tool, stdio process)
**Project Type**: CLI tool + MCP server (single Python package)
**Performance Goals**: Parse 100+ highlight files in <5 seconds (SC-001)
**Constraints**: Non-recursive directory scan; `.md` files only; per-file error tolerance
**Scale/Scope**: Single-user personal tool; no concurrency requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | ✅ PASS | Add `otb md count <path>` — Principle I is mandatory |
| II. Shared Parser Contract | ✅ PASS | Delegates to `parse_highlight_md` |
| III. Test-First | ✅ PASS | Tests written before implementation |
| IV. Type Safety & Lint | ✅ PASS | Full mypy + pylint compliance |
| V. Simplicity | ✅ PASS | Zero new deps; per-file errors in handler |
| VI. MCP Server | ✅ PASS | One new tool added to the existing server |

All gates pass. No Complexity Tracking entries required.

## Design Note: Per-File Error Tolerance (FR-006)

The existing `parse_highlight_dir` raises on the first bad file. For the MCP tool,
errors must not abort the whole call. The tool handler will iterate over `.md` files
directly, calling `parse_highlight_md` in a try/except per file, and collect both
successes and failures. The response includes a `highlights` list and a `parse_errors`
dict mapping filenames to error messages.

`parse_highlight_dir` in `md_parser.py` is left unchanged — it is used by callers
(e.g., CLI) that prefer fail-fast behaviour.

## Project Structure

### Documentation (this feature)

```text
specs/002-parse-md-highlights/
├── plan.md    # This file
├── tasks.md   # Phase 2 output (/speckit-tasks command)
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/otb/
├── cli.py           # add: otb md group + otb md count command
├── mcp_server.py    # add: parse_md_highlights_dir tool
└── md_parser.py     # unchanged

tests/
├── fixtures/highlights/   # existing fixtures (reused)
├── test_mcp_server.py     # add: parse_md_highlights_dir tool tests
└── test_md_parser.py      # unchanged
```

**Structure Decision**: All changes are additions to existing files. No new source
files or directories needed.

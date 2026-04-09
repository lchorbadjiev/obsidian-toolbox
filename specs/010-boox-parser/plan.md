# Implementation Plan: Boox Annotation Parser

**Branch**: `010-boox-parser` | **Date**: 2026-04-09 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/010-boox-parser/spec.md`

**Note**: This template is filled in by the `/speckit.plan`
command. See `.specify/templates/plan-template.md` for the
execution workflow. Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add a `boox_parser.py` module that reads Boox e-reader annotation
exports (a `book.txt` metadata file + a `.txt` annotation file)
and returns `list[Annotation]`. The parser reuses
`parse_book_metadata` from `zotero_parser.py` for book metadata
and implements a line-based state machine for the annotation text
file. A CLI command `otb boox parse` and an MCP tool
`parse_boox_export` expose the parser, following the same patterns
as the Zotero equivalents.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: None new — uses existing `click`, `mcp`
(FastMCP)
**Storage**: Filesystem (reads Boox export dirs, writes markdown)
**Testing**: pytest with fixture files in `tests/fixtures/boox/`
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A (small files, < 1s parse)
**Constraints**: No new dependencies (Constitution Principle V)
**Scale/Scope**: Single parser module, ~100-150 lines

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | `otb boox parse` command planned |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Fixtures in `tests/fixtures/boox/` |
| IV. Type Safety and Lint | PASS | Will satisfy mypy + pylint 10/10 |
| V. Simplicity | PASS | No new dependencies; stdlib only for parsing |
| VI. MCP Server | PASS | `parse_boox_export` MCP tool planned |
| VII. Document Formatting | PASS | All docs wrapped at 80 chars |

No violations. Complexity Tracking table not needed.

## Project Structure

### Documentation (this feature)

```text
specs/010-boox-parser/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/otb/
├── boox_parser.py          # NEW: Boox annotation parser
├── cli.py                  # MODIFY: add `otb boox parse`
├── mcp_server.py           # MODIFY: add parse_boox_export tool
├── parser.py               # EXISTING: Book, Annotation (no changes)
└── zotero_parser.py        # EXISTING: reuse parse_book_metadata

tests/
├── fixtures/
│   └── boox/               # NEW: Boox fixture directory
│       ├── book.txt
│       └── annotations.txt
└── test_boox_parser.py     # NEW: parser tests
```

**Structure Decision**: Single module added to existing `src/otb/`
package, following the established pattern of one parser per
source format (parser.py for Kindle HTML, md_parser.py for
markdown, zotero_parser.py for Zotero). Fixture directory follows
the existing `tests/fixtures/<source>/` convention.

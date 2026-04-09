# Implementation Plan: Merge Split Zotero Annotations

**Branch**: `014-merge-split-annotations` | **Date**: 2026-04-09
| **Spec**: [spec.md](spec.md)

**Note**: Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add a merge pass to the Zotero parser that detects consecutive
annotations on adjacent pages and merges them when the PDF text
confirms the highlighted passages are adjacent. Uses pypdf (already
a dependency) for page text extraction.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `pypdf` (already installed)
**Storage**: Filesystem (reads PDF for text extraction)
**Testing**: pytest
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A
**Constraints**: No new dependencies
**Scale/Scope**: New function in `pdf_figures.py` + merge pass
in `zotero_parser.py` (~50 lines)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | Works via `otb zotero parse` |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Tests planned |
| IV. Type Safety | PASS | mypy + pylint 10/10 |
| V. Simplicity | PASS | No new deps |
| VI. MCP Server | PASS | Transparent to MCP |
| VII. Doc Formatting | PASS | Wrapped at 80 chars |

No violations.

## Project Structure

### Source Code

```text
src/otb/
├── pdf_figures.py       # MODIFY: add text extraction helper
└── zotero_parser.py     # MODIFY: add merge pass

tests/
└── test_pdf_figures.py  # MODIFY: add merge tests
```

**Structure Decision**: Add merge logic as a function in
`pdf_figures.py` (already has pypdf dependency) called from
`zotero_parser.py` after initial parsing but before figure
extraction and numbering.

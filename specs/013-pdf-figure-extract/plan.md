# Implementation Plan: Extract PDF Figures for Zotero Annotations

**Branch**: `013-pdf-figure-extract` | **Date**: 2026-04-09 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/013-pdf-figure-extract/spec.md`

**Note**: Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add PDF figure extraction to the Zotero annotation workflow.
When a PDF file is present alongside a Zotero export, the system
detects figure references in annotations, renders the
corresponding PDF pages as PNG screenshots, saves them to an
`images/` subdirectory, and embeds image links in the annotation
markdown. Reuses the `FigureRef` dataclass from the EPUB figure
feature.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `pypdf` (NEW — PDF image extraction,
pure Python, no binary deps)
**Storage**: Filesystem (reads PDF, writes PNG images + markdown)
**Testing**: pytest with fixture files
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A (< 1s per page render)
**Constraints**: New dependency justified — PDF image extraction
is impossible with stdlib (Constitution Principle V exception).
pypdf is pure Python with no binary deps — lightweight choice.
**Scale/Scope**: New module `pdf_figures.py` (~100 lines) +
modifications to `zotero_parser.py`, `cli.py`, `mcp_server.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | `otb zotero parse` gains figure extraction |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Tests planned |
| IV. Type Safety | PASS | mypy + pylint 10/10 target |
| V. Simplicity | JUSTIFIED | pypdf required (pure Python) |
| VI. MCP Server | PASS | `parse_zotero_export` updated |
| VII. Doc Formatting | PASS | Docs wrapped at 80 chars |

## Complexity Tracking

| Violation | Why Needed | Rejected Because |
|-----------|------------|------------------|
| pypdf | PDF image extraction | stdlib cannot read PDFs |

## Project Structure

### Source Code (repository root)

```text
src/otb/
├── pdf_figures.py       # NEW: PDF figure extraction
├── zotero_parser.py     # MODIFY: figure detection + PDF path
├── cli.py               # MODIFY: pass figure data
├── mcp_server.py        # MODIFY: persist figures in MCP flow
└── md_writer.py         # EXISTING: already supports figures

tests/
├── fixtures/
│   └── zotero/
│       └── test.pdf     # NEW: minimal test PDF with figure
└── test_pdf_figures.py  # NEW: PDF figure tests
```

**Structure Decision**: New `pdf_figures.py` module parallel to
`epub_figures.py`. The Zotero parser calls into it when a PDF is
detected, following the same pattern as the Boox/EPUB workflow.

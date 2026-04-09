# Implementation Plan: Extract EPUB Figures for Annotations

**Branch**: `011-epub-figure-extract` | **Date**: 2026-04-09 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/011-epub-figure-extract/spec.md`

**Note**: Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add figure extraction to the Boox annotation workflow. When an
EPUB file is present alongside a Boox export, the system parses
the EPUB's XHTML to build a figure-id-to-image mapping, detects
figure references in annotation text (both captions and inline),
extracts the corresponding images, saves them to an `images/`
subdirectory, and embeds image links in the annotation markdown.
The EPUB is optional — the parser falls back to the existing
behavior when no EPUB is present.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `beautifulsoup4` (already installed,
for EPUB XHTML parsing), `zipfile` (stdlib, for EPUB extraction)
**Storage**: Filesystem (reads EPUB ZIP, writes images + markdown)
**Testing**: pytest with fixture files in `tests/fixtures/boox/`
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A (small files, < 1s per EPUB)
**Constraints**: No new dependencies (Constitution Principle V)
**Scale/Scope**: New module `epub_figures.py` (~150 lines) +
modifications to `boox_parser.py`, `md_writer.py`, `cli.py`,
`mcp_server.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | `otb boox parse` gains figure extraction |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` unchanged |
| III. Test-First | PASS | Fixture-based tests planned |
| IV. Type Safety | PASS | mypy + pylint 10/10 target |
| V. Simplicity | PASS | Uses bs4 (existing) + zipfile (stdlib) |
| VI. MCP Server | PASS | `parse_boox_export` unchanged |
| VII. Doc Formatting | PASS | All docs wrapped at 80 chars |

No violations. Complexity Tracking table not needed.

## Project Structure

### Documentation (this feature)

```text
specs/011-epub-figure-extract/
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
├── epub_figures.py      # NEW: EPUB figure extraction
├── boox_parser.py       # MODIFY: pass epub_path to extraction
├── md_writer.py         # MODIFY: append image links
├── cli.py               # MODIFY: pass images through
└── mcp_server.py        # MODIFY: support figure extraction

tests/
├── fixtures/
│   └── boox/
│       ├── book.txt              # EXISTING
│       ├── annotations.txt       # EXISTING
│       └── test.epub             # NEW: minimal test EPUB
└── test_epub_figures.py          # NEW: figure extraction tests
```

**Structure Decision**: New `epub_figures.py` module keeps figure
extraction logic separate from the Boox parser. The Boox parser
calls into it when an EPUB is detected. The md_writer is extended
to accept optional image metadata for embedding links.

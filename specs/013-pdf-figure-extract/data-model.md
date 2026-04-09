# Data Model: PDF Figure Extraction

**Feature**: 013-pdf-figure-extract
**Date**: 2026-04-09

## Reused Entities (no changes)

### FigureRef (in `src/otb/parser.py`)

Reused as-is from the EPUB figure feature.

| Field      | Type | Description                           |
|------------|------|---------------------------------------|
| label      | str  | Figure label (e.g., "5-2", "2-1")    |
| image_path | str  | Relative path to extracted image      |

### Annotation (in `src/otb/parser.py`)

Reused as-is. The `figures` field already exists.

## New Module: pdf_figures.py

### PdfFigureMap

Same type alias as `FigureMap` from `epub_figures.py`:
`dict[str, tuple[bytes, str]]` — label to (image_bytes, ext).

### Functions

| Function | Description |
|----------|-------------|
| `extract_page_image` | Extract largest image from a page |
| `extract_pdf_figures` | Extract images for all figure refs |
| `detect_zotero_figure_refs` | Detect figure refs with pages |

## Figure Detection Patterns (Zotero-specific)

| Pattern | Regex | Example Match |
|---------|-------|---------------|
| Caption | `^Figure\s+(\d+[-.]?\d+)` | "Figure 5-2." |
| Inline | `Figure\s+(\d+[-.]?\d+)` | "Figure 2-1" |
| Request | `[Gg]et the figure\s+(\d+[-.]?\d+)` | "Get the figure 5-17" |

## Processing Pipeline

```text
Zotero Export Directory
├── book.txt
├── Annotations.md
└── book.pdf (optional)
        │
        ▼
┌─────────────────────┐
│ zotero_parser.py     │
│ parse_zotero_annotations() │
│ - detect figure refs │
│ - extract from PDF   │
│ - attach FigureRef   │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ md_writer.py         │
│ write_annotation()   │
│ - write images/      │
│ - embed image links  │
└─────────────────────┘
```

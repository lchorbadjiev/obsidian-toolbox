# Data Model: Extract EPUB Figures for Annotations

**Feature**: 011-epub-figure-extract
**Date**: 2026-04-09

## Modified Entities

### Annotation (in `src/otb/parser.py`)

New optional field added to the existing dataclass.

| Field   | Type              | Description                    |
|---------|-------------------|--------------------------------|
| figures | list of FigureRef | Figures referenced (default []) |

All other fields unchanged. Existing parsers (Kindle, Zotero,
markdown) produce annotations with an empty `figures` list,
preserving backward compatibility.

### FigureRef (new, in `src/otb/parser.py`)

Represents a single figure extracted from an EPUB.

| Field      | Type | Description                           |
|------------|------|---------------------------------------|
| label      | str  | Figure label (e.g., "2.1", "7.9b")   |
| image_path | str  | Relative path to extracted image file |

## New Entities

### EpubFigureMap (in `src/otb/epub_figures.py`)

A mapping from figure labels to image data, built by parsing
an EPUB's XHTML content.

| Field       | Type                 | Description             |
|-------------|----------------------|-------------------------|
| figures     | dict of str to bytes | label → image bytes     |
| extensions  | dict of str to str   | label → file extension  |

### Processing Pipeline

```text
Boox Export Directory
├── book.txt
├── annotations.txt
└── book.epub (optional)
        │
        ▼
┌─────────────────────┐
│ epub_figures.py      │
│ parse_epub_figures() │
│ → EpubFigureMap      │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ boox_parser.py       │
│ parse_boox_annotations() │
│ - detect figure refs │
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

## Field Mapping: Figure Reference → FigureRef

| Source                        | FigureRef Field | Notes               |
|-------------------------------|-----------------|----------------------|
| Regex match on annotation text | label          | "2.1", "7.9b", etc. |
| EPUB image data via map       | image_path     | Set during write     |

## Figure Detection Patterns

| Pattern | Regex | Example Match |
|---------|-------|---------------|
| Caption | `^FIGURE\s+(\d+\.\d+[a-z]?)` | "FIGURE 2.1." |
| Inline | `Figure\s+(\d+\.\d+[a-z]?)` | "(Figure 2.3)" |

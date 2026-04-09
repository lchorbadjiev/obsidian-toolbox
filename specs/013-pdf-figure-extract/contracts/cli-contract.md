# CLI Contract: PDF Figure Extraction

**Feature**: 013-pdf-figure-extract
**Date**: 2026-04-09

## Modified Command: `otb zotero parse`

### Synopsis (unchanged)

```text
otb zotero parse INPUT_DIR OUTPUT_DIR [--verbose]
```

### New Behavior

When INPUT_DIR contains a `.pdf` file alongside the Zotero
export files, the command:

1. Parses annotations as before.
2. Detects figure references in annotation text.
3. Renders referenced PDF pages as PNG screenshots.
4. Saves screenshots to `OUTPUT_DIR/images/`.
5. Embeds image links in annotation markdown files.

When no `.pdf` is present, behavior is identical to before.

### Output Structure

```text
OUTPUT_DIR/
├── 001 - Title.md
├── 002 - Title.md
├── ...
└── images/
    ├── figure-2-1.png
    ├── figure-5-2.png
    └── ...
```

### Warnings (stderr)

- `Warning: PDF unreadable: {path}` — corrupted PDF
- `Warning: Figure {label} page {n} out of range` — bad page

## Modified MCP Tool: `parse_zotero_export`

### New Response Fields

Each annotation dict gains an optional `figures` field
(same as Boox export):

```json
{
  "figures": [
    {"label": "5-2", "image_path": "images/figure-5-2.png"}
  ]
}
```

The tool also returns `figures_dir` when a PDF is present
(temp dir with rendered page screenshots), matching the
Boox export pattern.

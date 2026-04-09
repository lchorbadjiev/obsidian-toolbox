# CLI Contract: EPUB Figure Extraction

**Feature**: 011-epub-figure-extract
**Date**: 2026-04-09

## Modified Command: `otb boox parse`

### Synopsis (unchanged)

```text
otb boox parse INPUT_DIR OUTPUT_DIR
```

### New Behavior

When INPUT_DIR contains an `.epub` file alongside the Boox
export files, the command:

1. Parses the EPUB to build a figure-id-to-image mapping.
2. Detects figure references in annotation text.
3. Extracts referenced images to `OUTPUT_DIR/images/`.
4. Embeds image links in annotation markdown files.

When no `.epub` is present, behavior is identical to before.

### Output Structure

```text
OUTPUT_DIR/
├── 001 - Title.md          # annotation with image link
├── 002 - Title.md          # annotation without figures
├── ...
└── images/
    ├── figure-2-1.jpg      # extracted figure image
    ├── figure-2-3.jpg
    └── ...
```

### Image Link Format in Markdown

```markdown
> Annotation text here...

![Figure 2.1](images/figure-2-1.jpg)
```

### Warnings (stderr)

- `Warning: EPUB unreadable: {path}` — corrupted EPUB
- `Warning: Figure {label} not found in EPUB` — missing image

## Modified MCP Tool: `parse_boox_export`

### New Response Fields

Each annotation dict gains an optional `figures` field:

```json
{
  "figures": [
    {"label": "2.1", "image_path": "images/figure-2-1.jpg"}
  ]
}
```

When no figures are detected, `figures` is an empty list.

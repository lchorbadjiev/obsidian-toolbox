# Data Model: Parse Zotero Annotations

**Feature**: 006-parse-zotero-annotations
**Date**: 2026-04-06

## Existing Entities (no changes)

### Book

Defined in `src/otb/parser.py`. No modifications needed.

| Field  | Type | Description             |
|--------|------|-------------------------|
| title  | str  | Book title              |
| author | str  | Author in display order |

### Annotation

Defined in `src/otb/parser.py`. No modifications needed.

| Field    | Type          | Zotero mapping                   |
|----------|---------------|----------------------------------|
| book     | Book          | From `book.txt`                  |
| chapter  | str           | Empty string (not available)     |
| page     | int           | From `("Title", p. XX)`          |
| location | int           | Same as page (per clarification) |
| text     | str           | Quoted text from annotation      |
| title    | str           | Auto-generated (7 words)         |
| color    | str or None   | None (not available)             |
| number   | int           | Sequential, starting at 1        |
| anki_id  | int or None   | None (not set by parser)         |

## Data Flow

```text
book.txt ──────────────────┐
                           ├──► zotero_parser ──► list[Annotation]
Annotations.md ────────────┘         │
                                     ▼
                              md_writer.write_annotations()
                                     │
                                     ▼
                              output_dir/
                              ├── 001 - Title One.md
                              ├── 002 - Title Two.md
                              └── ...
```

## Validation Rules

- `book.txt` MUST contain a `Title` field and an `Authors`
  field (or parsing fails with an error).
- Each annotation MUST have a quoted string and a page
  reference. Annotations without page references are skipped
  with a warning.
- Page numbers MUST be parseable as integers.
- Empty annotations (blank quoted strings) are skipped.

# Data Model: Boox Annotation Parser

**Feature**: 010-boox-parser
**Date**: 2026-04-09

## Existing Entities (no changes)

### Book

Defined in `src/otb/parser.py`. Used as-is.

| Field  | Type | Description           |
|--------|------|-----------------------|
| title  | str  | Book title            |
| author | str  | Author name(s)        |

### Annotation

Defined in `src/otb/parser.py`. Used as-is.

| Field    | Type         | Description                    |
|----------|--------------|--------------------------------|
| book     | Book         | Reference to parent book       |
| chapter  | str          | Chapter heading (may be empty) |
| page     | str          | Empty string for Boox          |
| location | int          | Page number from Boox export   |
| text     | str          | Highlighted passage text       |
| title    | str          | Auto-generated from first sentence |
| color    | str or None  | Always None for Boox           |
| number   | int          | Sequential 1-based index       |
| anki_id  | int or None  | Not set by parser              |

## Field Mapping: Boox Export → Annotation

| Boox Source                   | Annotation Field | Notes                    |
|-------------------------------|------------------|--------------------------|
| `book.txt` Title/Authors      | book             | Via `parse_book_metadata` |
| Standalone line before date   | chapter          | Tracked as current state  |
| (not available)               | page             | Set to empty string       |
| `Page No.: NNN`               | location         | Extracted as integer      |
| Text lines before separator   | text             | Joined with space         |
| First sentence of text        | title            | Via `_title_from_text`    |
| (not available)               | color            | Set to None               |
| Sequential counter            | number           | 1-based, set after parse  |

## State Machine

The parser processes lines sequentially with these states:

1. **HEADER** → skip first line (starts with "Reading Notes")
2. **BETWEEN** → after separator or header; looking for chapter
   heading or date/page line
3. **IN_ANNOTATION** → collecting text lines until next separator

Transitions:

- HEADER → BETWEEN (after first line)
- BETWEEN + chapter line → BETWEEN (update current chapter)
- BETWEEN + date/page line → IN_ANNOTATION (start new annotation)
- IN_ANNOTATION + separator → BETWEEN (finalize annotation)
- IN_ANNOTATION + text line → IN_ANNOTATION (append to text)
- IN_ANNOTATION + EOF → BETWEEN (finalize last annotation)

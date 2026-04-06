# Data Model: Improve Kindle Import MCP Tools

**Date**: 2026-04-06
**Feature**: 009-kindle-import-file-passing

## Entities

### Annotation (unchanged)

The `Annotation` dataclass in `src/otb/parser.py` is not
modified. All fields remain the same:

- `book`: `Book` (title, author)
- `chapter`: `str`
- `page`: `str`
- `location`: `int`
- `text`: `str`
- `title`: `str` (default `""`)
- `color`: `str | None` (default `None`)
- `number`: `int` (default `0`)

### Annotation Dict (serialization format)

The JSON serialization produced by `_annotation_to_dict` is
the format used in the temp file. Each object has:

- `book_title`: `str`
- `author`: `str`
- `chapter`: `str`
- `page`: `str`
- `location`: `int`
- `text`: `str`
- `title`: `str` (empty from parse, filled after title gen)
- `color`: `str | null`
- `number`: `int`

### Temp Annotations File (new)

A JSON file containing an array of annotation dict objects.
Written by `parse_kindle_export`, read by `save_annotations`.

- **Location**: System temp directory
  (`tempfile.gettempdir()`)
- **Naming**: Auto-generated unique name with `.json` suffix
- **Lifecycle**: Created by parse tool, persists until OS
  cleanup or manual deletion
- **Format**: `[{annotation_dict}, ...]`

### Parse Summary (new return type)

The return value of the refactored `parse_kindle_export`:

- `file_path`: `str` — absolute path to the temp JSON file
- `count`: `int` — total number of annotations parsed
- `book_title`: `str` — title of the book
- `author`: `str` — author name (normalized)
- `chapters`: `list[str]` — ordered list of unique chapters

## Relationships

```text
Kindle HTML → parse_kindle_export → Temp JSON File
                                         ↓
                              (LLM reads/writes titles)
                                         ↓
                              save_annotations ← Temp JSON File
                                         ↓
                              Markdown Files (one per annotation)
```

## State Transitions

The temp file goes through these states:

1. **Created**: Written by `parse_kindle_export` with all
   `title` fields empty
2. **Titles added**: LLM subagents read batches, generate
   titles, write updated annotations back
3. **Consumed**: `save_annotations` reads the file and
   writes markdown files
4. **Orphaned**: File remains in temp dir until OS cleanup
   (no explicit deletion by tools)

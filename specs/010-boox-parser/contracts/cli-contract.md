# CLI Contract: Boox Parser

**Feature**: 010-boox-parser
**Date**: 2026-04-09

## Command: `otb boox parse`

### Synopsis

```text
otb boox parse INPUT_DIR OUTPUT_DIR
```

### Arguments

| Argument   | Type      | Required | Description                          |
|------------|-----------|----------|--------------------------------------|
| INPUT_DIR  | directory | yes      | Directory containing Boox export     |
| OUTPUT_DIR | directory | yes      | Directory for markdown output        |

### Behavior

1. Reads `book.txt` and the annotation `.txt` file from
   INPUT_DIR.
2. Parses annotations into `list[Annotation]`.
3. Writes markdown files to OUTPUT_DIR using existing
   `md_writer` module.
4. Prints annotation count to stdout.
5. Errors go to stderr.

### Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Success                              |
| 1    | Missing required files in INPUT_DIR  |
| 2    | No annotations found                 |

## MCP Tool: `parse_boox_export`

### Parameters

| Parameter | Type   | Required | Description                    |
|-----------|--------|----------|--------------------------------|
| path      | string | yes      | Path to Boox export directory  |

### Response

Returns a list of annotation dictionaries, each containing:
`book_title`, `book_author`, `chapter`, `page`, `text`,
`title`, `number`.

### Errors

- Directory not found → error message
- Missing `book.txt` → error message
- No annotation file found → error message

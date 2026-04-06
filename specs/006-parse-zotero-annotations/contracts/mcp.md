# MCP Contract: Zotero Tool

**Feature**: 006-parse-zotero-annotations
**Date**: 2026-04-06

## Tool: `parse_zotero_export`

**Description**: Parse a Zotero annotation export directory and
return the list of annotations.

### Input Schema

| Parameter | Type   | Required | Description                     |
|-----------|--------|----------|---------------------------------|
| path      | string | Yes      | Path to Zotero export directory |

### Output

Returns `list[dict]` where each dict contains:

```json
{
  "book_title": "string",
  "book_author": "string",
  "chapter": "",
  "page": 42,
  "location": 42,
  "text": "string",
  "title": "string",
  "color": null,
  "number": 1,
  "anki_id": null
}
```

### Error Conditions

| Condition                    | Error Type         |
|------------------------------|--------------------|
| Directory does not exist     | FileNotFoundError  |
| Missing `Annotations.md`     | FileNotFoundError  |
| Missing `book.txt`           | FileNotFoundError  |
| Path is not a directory      | NotADirectoryError |

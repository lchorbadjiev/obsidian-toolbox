# MCP Contract: Zotero Tool (Updated)

**Feature**: 007-fix-zotero-word-concat
**Date**: 2026-04-06

## Tool: `parse_zotero_export` (updated behavior)

**Description**: Parse a Zotero annotation export directory
and return the list of annotations with concatenated words
automatically fixed.

### Input Schema (unchanged)

| Parameter | Type   | Required | Description                   |
|-----------|--------|----------|-------------------------------|
| path      | string | Yes      | Path to Zotero export dir     |

### Output (unchanged structure)

Returns `list[dict]` — same schema as 006. The `text` field
now contains cleaned text with concatenated words split.

### Updated Error Conditions

| Condition                  | Error Type         |
|----------------------------|--------------------|
| Directory does not exist   | FileNotFoundError  |
| Missing `Annotations.md`  | FileNotFoundError  |
| Missing `book.txt`        | FileNotFoundError  |
| Path is not a directory    | NotADirectoryError |
| aspell not installed       | RuntimeError       |

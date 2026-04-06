# MCP Tool Contracts: Kindle Import File Passing

**Date**: 2026-04-06
**Feature**: 009-kindle-import-file-passing

## parse_kindle_export

### Before (current)

```text
Input:  path: str (absolute path to Kindle HTML file)
Output: list[dict] (full annotation array)
Errors: FileNotFoundError if path doesn't exist
```

### After (planned)

```text
Input:  path: str (absolute path to Kindle HTML file)
Output: dict with keys:
  - file_path: str (absolute path to temp JSON file)
  - count: int (number of annotations)
  - book_title: str
  - author: str
  - chapters: list[str] (unique chapters in order)
Errors: FileNotFoundError if path doesn't exist
Side effect: writes temp JSON file containing
  list[annotation_dict]
```

## save_annotations

### Before (current)

```text
Input:
  - annotations: list[dict] (annotation dicts)
  - directory: str (target directory)
Output: list[str] (file paths written)
Errors: OSError on write failure
```

### After (planned)

```text
Input (mutually exclusive — exactly one required):
  - annotations: list[dict] | None (annotation dicts)
  - file_path: str | None (path to JSON file)
  Plus:
  - directory: str (target directory)
Output: list[str] (file paths written)
Errors:
  - ValueError if both annotations and file_path provided
  - ValueError if neither annotations nor file_path provided
  - FileNotFoundError if file_path doesn't exist
  - OSError on write failure
```

## kindle_import_annotations (MCP prompt)

### Before (current)

```text
Steps:
1. parse_kindle_export(path=X) → full annotation list
2. Generate titles for each annotation
3. save_annotations(annotations=<list>, directory=Y)
```

### After (planned)

```text
Steps:
1. parse_kindle_export(path=X) → {file_path, count, ...}
2. Read temp file in batches of ~30, generate titles via
   subagents, write titles back to temp file
3. save_annotations(file_path=<path>, directory=Y)
```

# MCP Contract: Kindle Import Annotations Prompt

**Feature**: 008-kindle-import-prompt
**Date**: 2026-04-06

## Prompt: `kindle-import-annotations`

**Description**: Import Kindle annotations from an HTML
export file, generate titles for each annotation, and
save them as individual markdown files.

### Input Schema

| Parameter | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| file_path | string | Yes      | Path to Kindle HTML file |

The output directory is derived automatically as `notes/`
inside the parent directory of `file_path`.

### Output

Returns `list[UserMessage]` containing step-by-step
instructions for the MCP client to execute:

1. Call `parse_kindle_export(path=file_path)`
2. Generate a title for each annotation
3. Call `save_annotations(annotations, <derived dir>)`

### Error Conditions

The prompt itself does not raise errors — it builds
instruction text. Errors occur when the MCP client
executes the referenced tools:

| Condition              | Tool                 | Error            |
|------------------------|----------------------|------------------|
| File not found         | parse_kindle_export  | FileNotFoundError |
| Invalid HTML           | parse_kindle_export  | ValueError       |
| Write failure          | save_annotations     | OSError          |

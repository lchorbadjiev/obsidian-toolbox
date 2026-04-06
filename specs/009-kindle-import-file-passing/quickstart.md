# Quickstart: Improve Kindle Import MCP Tools

**Date**: 2026-04-06
**Feature**: 009-kindle-import-file-passing

## What Changes

Two MCP tools (`parse_kindle_export`, `save_annotations`)
and one MCP prompt (`kindle_import_annotations`) in
`src/otb/mcp_server.py` are modified to pass annotation data
via temp JSON files instead of inline arrays.

## Files to Modify

1. **`src/otb/mcp_server.py`** — Refactor `parse_kindle_export`
   to write temp file and return summary. Add `file_path`
   parameter to `save_annotations`. Update
   `kindle_import_annotations` prompt text.

2. **`tests/test_mcp_server.py`** — Add tests for temp file
   creation, summary return format, `file_path` parameter,
   mutual exclusion error, and updated prompt content.

## Implementation Order

1. Write failing tests for `parse_kindle_export` changes
2. Implement `parse_kindle_export` temp file output
3. Write failing tests for `save_annotations` `file_path`
4. Implement `save_annotations` `file_path` parameter
5. Update `kindle_import_annotations` prompt text
6. Update prompt tests
7. Run full quality gates: pytest, mypy, pylint

## Key Design Decisions

- Use `tempfile.NamedTemporaryFile(delete=False, suffix=".json")`
- Return dict summary from parse (path, count, metadata)
- `annotations` and `file_path` are mutually exclusive on save
- Prompt recommends ~30-annotation batches for title generation
- No new dependencies (stdlib `json` + `tempfile` only)

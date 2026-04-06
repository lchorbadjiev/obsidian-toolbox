# Quickstart: Kindle Import Annotations Prompt

**Feature**: 008-kindle-import-prompt
**Date**: 2026-04-06

## Prerequisites

```bash
uv sync
```

## Usage

### MCP

The `kindle-import-annotations` prompt is available via
the MCP server:

```bash
otb mcp
```

When connected to an MCP client (e.g., Claude), invoke
the prompt:

> Use the `kindle-import-annotations` prompt with
> file_path `~/Downloads/My Book - Notebook.html`

Annotations are saved to `~/Downloads/notes/`
automatically.

The MCP client will:

1. Call `parse_kindle_export` to read annotations.
2. Generate a concise title for each annotation.
3. Call `save_annotations` to write the markdown files.

## Development

### Run tests

```bash
uv run pytest tests/test_mcp_server.py -k "kindle_import"
```

### Type-check and lint

```bash
uv run mypy src/ tests/
uv run pylint src/ tests/
```

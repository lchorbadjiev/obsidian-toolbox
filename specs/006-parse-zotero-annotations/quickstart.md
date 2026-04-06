# Quickstart: Parse Zotero Annotations

**Feature**: 006-parse-zotero-annotations
**Date**: 2026-04-06

## Prerequisites

```bash
uv sync
```

## Usage

### CLI

```bash
# Parse Zotero annotations into individual markdown files
otb zotero parse ./path/to/zotero-export ./output-annotations/
```

The input directory must contain:

- `Annotations.md` -- Zotero annotation export
- `book.txt` -- Zotero book metadata export

### MCP

The `parse_zotero_export` tool is available via the MCP server:

```bash
otb mcp
```

## Development

### Run tests

```bash
uv run pytest tests/test_zotero_parser.py
uv run pytest tests/test_cli_zotero.py
```

### Type-check and lint

```bash
uv run mypy src/ tests/
uv run pylint src/ tests/
```

## File Layout

```text
src/otb/
├── zotero_parser.py   # New: Zotero annotation parser
├── cli.py             # Modified: add zotero command group
└── mcp_server.py      # Modified: add parse_zotero_export tool

tests/
├── test_zotero_parser.py  # New: parser unit tests
├── test_cli_zotero.py     # New: CLI integration tests
└── fixtures/zotero/       # Existing: test fixtures
    ├── Annotations.md
    └── book.txt
```

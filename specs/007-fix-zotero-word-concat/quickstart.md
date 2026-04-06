# Quickstart: Fix Zotero Word Concatenation

**Feature**: 007-fix-zotero-word-concat
**Date**: 2026-04-06

## Prerequisites

```bash
# Install aspell (macOS)
brew install aspell

# Install aspell (Ubuntu/Debian)
# sudo apt-get install aspell aspell-en

# Verify installation
aspell --version

# Install Python dependencies
uv sync
```

## Usage

### CLI

```bash
# Parse with automatic word-splitting (default)
otb zotero parse ./path/to/zotero-export ./output/

# Parse with verbose output (see each word fix)
otb zotero parse --verbose ./path/to/zotero-export ./output/
```

### MCP

The `parse_zotero_export` tool automatically applies
word-splitting:

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

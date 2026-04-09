# Quickstart: Boox Annotation Parser

**Feature**: 010-boox-parser
**Date**: 2026-04-09

## Prerequisites

- Python 3.12+
- `uv sync` (install dependencies)

## Development Workflow

### 1. Create test fixture

Copy the sample Boox export to the fixture directory:

```bash
mkdir -p tests/fixtures/boox
cp tmp/just-for-fun-torvalds/book.txt tests/fixtures/boox/
cp "tmp/just-for-fun-torvalds/Just for Fun_"*.txt \
   tests/fixtures/boox/annotations.txt
```

### 2. Write failing tests first (Constitution III)

```bash
# Create test_boox_parser.py with tests, then:
uv run pytest tests/test_boox_parser.py  # should FAIL (red)
```

### 3. Implement the parser

Create `src/otb/boox_parser.py` with `parse_boox_annotations`
function.

```bash
uv run pytest tests/test_boox_parser.py  # should PASS (green)
```

### 4. Add CLI command

Wire `otb boox parse` in `src/otb/cli.py`.

```bash
uv run pytest tests/test_cli.py  # verify CLI integration
```

### 5. Add MCP tool

Register `parse_boox_export` in `src/otb/mcp_server.py`.

```bash
uv run pytest tests/test_mcp_server.py  # verify MCP tool
```

### 6. Quality gates

```bash
uv run pytest                           # all tests pass
uv run mypy src/ tests/                 # zero errors
uv run pylint src/ tests/               # 10/10
pymarkdownlnt scan -r --respect-gitignore .  # zero errors
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/boox_parser.py` | Parser implementation |
| `src/otb/cli.py` | CLI command `otb boox parse` |
| `src/otb/mcp_server.py` | MCP tool `parse_boox_export` |
| `tests/test_boox_parser.py` | Parser unit/integration tests |
| `tests/fixtures/boox/` | Test fixture files |

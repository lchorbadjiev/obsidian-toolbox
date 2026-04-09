# Quickstart: Boox Import Annotations Prompt

**Feature**: 012-boox-import-prompt
**Date**: 2026-04-09

## Development Workflow

### 1. Write failing tests first (Constitution III)

```bash
uv run pytest tests/test_mcp_server.py -k boox_import
# should FAIL (red)
```

### 2. Implement the prompt

Add `boox_import_annotations` function to
`src/otb/mcp_server.py`, decorated with `@mcp.prompt`.

```bash
uv run pytest tests/test_mcp_server.py -k boox_import
# should PASS (green)
```

### 3. Quality gates

```bash
uv run pytest
uv run mypy src/ tests/
uv run pylint src/ tests/
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/mcp_server.py` | Add prompt function |
| `tests/test_mcp_server.py` | Add prompt tests |

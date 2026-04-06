# Implementation Plan: Improve Kindle Import MCP Tools

**Branch**: `009-kindle-import-file-passing` | **Date**: 2026-04-06
| **Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/009-kindle-import-file-passing/spec.md`

Prose lines MUST wrap at 80 characters (Constitution Principle VII).

## Summary

Refactor `parse_kindle_export` and `save_annotations` MCP tools
to pass annotation data via temporary JSON files instead of
inline arrays. This eliminates the 113K+ token explosion that
breaks large Kindle imports (166+ annotations). The parse tool
writes annotations to a temp file and returns a lightweight
summary; the save tool accepts a `file_path` parameter to read
from that file. The MCP prompt is updated to orchestrate this
file-based workflow with ~30-annotation batches for title
generation.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: mcp (FastMCP), click, beautifulsoup4
**Storage**: Filesystem (temp JSON files, markdown output)
**Testing**: pytest with fixtures in `tests/fixtures/`
**Target Platform**: macOS/Linux (stdio MCP transport)
**Project Type**: CLI + MCP server
**Performance Goals**: N/A (batch processing, not real-time)
**Constraints**: No new dependencies (Constitution V)
**Scale/Scope**: Tested with 166 annotations; should handle
any reasonable Kindle export size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | No new CLI commands needed; existing `otb mcp` serves the MCP tools |
| II. Shared Parser Contract | PASS | Still produces `list[Annotation]` via `parse_notebook`; temp file uses same schema |
| III. Test-First | PASS | New tests for file-path parameters, temp file writing, error cases |
| IV. Type Safety & Lint | PASS | All new code will be typed; mypy + pylint gates apply |
| V. Simplicity & Minimal Deps | PASS | Uses only `json`, `tempfile` from stdlib; no new deps |
| VI. MCP Server (stdio) | PASS | Tools remain MCP-registered; transport unchanged |
| VII. Document Formatting | PASS | All docs wrapped at 80 chars |

## Project Structure

### Documentation (this feature)

```text
specs/009-kindle-import-file-passing/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp-tools.md
└── tasks.md
```

### Source Code (repository root)

```text
src/otb/
├── mcp_server.py        # Modified: parse_kindle_export,
│                        #   save_annotations,
│                        #   kindle_import_annotations
├── parser.py            # Unchanged
└── md_writer.py         # Unchanged

tests/
├── test_mcp_server.py   # Modified: new tests for file-path
│                        #   params, temp file output, errors
└── fixtures/            # Unchanged
```

**Structure Decision**: This is a modification to existing
files only. No new modules or directories needed. The MCP
server module (`mcp_server.py`) and its test file are the
only source files affected.

## Complexity Tracking

> No constitution violations. Table not needed.

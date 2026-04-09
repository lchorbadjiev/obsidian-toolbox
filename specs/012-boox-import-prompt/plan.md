# Implementation Plan: Boox Import Annotations Prompt

**Branch**: `012-boox-import-prompt` | **Date**: 2026-04-09 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/012-boox-import-prompt/spec.md`

**Note**: Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add a `boox_import_annotations` MCP prompt that returns
step-by-step instructions for importing Boox annotations,
following the same pattern as the existing
`kindle_import_annotations` prompt. The workflow: parse via
`parse_boox_export`, generate titles with a lightweight model,
then save via `save_annotations`.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `mcp` (FastMCP) — already installed
**Storage**: N/A (prompt returns instructions, no I/O)
**Testing**: pytest
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A (prompt generation is instant)
**Constraints**: No new dependencies (Constitution Principle V)
**Scale/Scope**: Single function + decorator in `mcp_server.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | N/A | MCP prompt, not a CLI command |
| II. Shared Parser Contract | PASS | Uses existing tools |
| III. Test-First | PASS | Tests planned |
| IV. Type Safety | PASS | mypy + pylint 10/10 target |
| V. Simplicity | PASS | No new deps |
| VI. MCP Server | PASS | New MCP prompt registered |
| VII. Doc Formatting | PASS | All docs wrapped at 80 chars |

No violations. Complexity Tracking table not needed.

## Project Structure

### Source Code (repository root)

```text
src/otb/
└── mcp_server.py        # MODIFY: add boox_import_annotations

tests/
└── test_mcp_server.py   # MODIFY: add prompt tests
```

**Structure Decision**: Minimal change — one new function in
the existing MCP server module, following the identical pattern
of `kindle_import_annotations`.

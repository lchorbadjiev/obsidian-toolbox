# Implementation Plan: Kindle Import Annotations Prompt

**Branch**: `008-kindle-import-prompt` | **Date**: 2026-04-06
| **Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/008-kindle-import-prompt/spec.md`

Prose lines MUST wrap at 80 characters (Constitution
Principle VII).

## Summary

Add a new MCP prompt `kindle-import-annotations` that
takes a single `file_path` parameter and returns
step-by-step instructions for the MCP client to: (1) parse
the Kindle HTML export, (2) generate titles using a
lightweight AI subagent, (3) save all annotations to a
`notes/` subdirectory alongside the export file. The output
directory is derived automatically — no second parameter
needed.

## Technical Context

**Language/Version**: Python 3.12+ + mcp (FastMCP) —
already installed; no new deps
**Primary Dependencies**: None new
**Storage**: N/A (prompt returns text instructions)
**Testing**: pytest
**Target Platform**: MCP server (stdio transport)
**Project Type**: MCP server prompt
**Performance Goals**: N/A (prompt builds a text string)
**Constraints**: No new dependencies (Constitution
Principle V)
**Scale/Scope**: Single prompt function

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | N/A | Prompt-only; no CLI needed |
| II. Shared Contract | PASS | Uses existing dict format |
| III. Test-First | PASS | Tests planned first |
| IV. Type Safety | PASS | mypy + pylint maintained |
| V. Simplicity | PASS | No new deps |
| VI. MCP Server | PASS | New prompt via @mcp.prompt |
| VII. Doc Formatting | PASS | 80-char wrapping enforced |

No violations.

## Project Structure

### Documentation (this feature)

```text
specs/008-kindle-import-prompt/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mcp.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/otb/
├── mcp_server.py      # MODIFIED: update prompt function
└── ...

tests/
├── test_mcp_server.py # MODIFIED: update prompt tests
└── ...
```

**Structure Decision**: Minimal change — update the
existing prompt function in `mcp_server.py` to accept
only `file_path` and derive the output directory as
`notes/` inside the file's parent directory.

## Implementation Phases

### Phase 1: Update Prompt and Tests

1. Update tests in `tests/test_mcp_server.py`:
   - Change prompt call to single `file_path` parameter.
   - Assert output mentions `notes/` directory derivation.
   - Assert prompt text does NOT reference a `directory`
     parameter.

2. Update `src/otb/mcp_server.py`:
   - Change `kindle_import_annotations(file_path, directory)`
     to `kindle_import_annotations(file_path)`.
   - Derive output directory in prompt text as
     `<parent of file_path>/notes/`.

3. Verify: `uv run pytest tests/test_mcp_server.py -k
   kindle_import` green.

### Phase 2: Quality Gates

1. `uv run pytest` — all tests pass.
2. `uv run mypy src/ tests/` — zero errors.
3. `uv run pylint src/ tests/` — 10/10.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | N/A | Prompt-only; justified |
| II. Shared Contract | PASS | Uses existing dict format |
| III. Test-First | PASS | Tests updated first |
| IV. Type Safety | PASS | mypy + pylint clean |
| V. Simplicity | PASS | No new deps |
| VI. MCP Server | PASS | Prompt registered |
| VII. Doc Formatting | PASS | 80-char, lint clean |

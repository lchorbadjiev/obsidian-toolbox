# Implementation Plan: Kindle MCP Server

**Branch**: `001-kindle-mcp-server` | **Date**: 2026-04-05 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-kindle-mcp-server/spec.md`

## Summary

Add an MCP server (`otb mcp`) that exposes two tools to LLM agents: parse a Kindle
HTML export into raw highlights (no auto-titles), and save highlights as individual
markdown files. Title generation is delegated to the host LLM via tool description
guidance — no Anthropic SDK required. A new `md_writer.py` module handles markdown
output in a format round-trippable with the existing `md_parser.py`.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `click` (CLI), `beautifulsoup4` (HTML parsing), `mcp` (MCP
server) — one new runtime dependency; see Dependency Note below
**Storage**: Files (markdown files written to disk by the save tool)
**Testing**: pytest; MCP tool tests use direct function calls against tool handlers
**Target Platform**: macOS / Linux (personal tool, stdio process)
**Project Type**: CLI tool + MCP server (single Python package)
**Performance Goals**: Parse 100+ highlights in <5 seconds (SC-001; easily met by
in-process HTML parsing)
**Constraints**: stdio transport only; saved files must round-trip through `md_parser.py`
**Scale/Scope**: Single-user personal tool; no concurrency requirements

## Dependency Note

**One new runtime dependency**: `mcp` (MCP Python SDK).

Mandated by Constitution Principle VI and the Technology Stack. Provides FastMCP
high-level API for defining tools, handling stdio transport, and schema generation.

`anthropic` SDK is **not required** — title generation is
handled by the host LLM as part of its orchestration workflow
(FR-008), not by the server.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | ✅ PASS | `otb mcp` command added to `cli.py` |
| II. Shared Parser Contract | ✅ PASS | `list[Highlight]`; unchanged |
| III. Test-First | ✅ PASS | Tests before impl; MCP tests required |
| IV. Type Safety & Lint | ✅ PASS | Full mypy + pylint compliance enforced |
| V. Simplicity | ✅ PASS | Only `mcp` added; no pyyaml; no speculative features |
| VI. MCP Server | ✅ PASS | This feature implements the principle |

All gates pass. No Complexity Tracking entries required.

## Project Structure

### Documentation (this feature)

```text
specs/001-kindle-mcp-server/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
src/otb/
├── __init__.py
├── cli.py           # add: otb mcp command
├── parser.py        # modify: add generate_title param to parse_notebook
├── md_parser.py     # unchanged
├── md_writer.py     # new: write Highlight objects to markdown files
└── mcp_server.py    # new: FastMCP server with 2 tools

tests/
├── fixtures/
│   └── highlights/  # existing markdown fixtures (reused)
├── test_parser.py   # existing (add generate_title=False case)
├── test_md_parser.py  # existing
├── test_md_writer.py  # new
└── test_mcp_server.py # new
```

**Structure Decision**: Single project layout (existing `src/otb` package). No new
top-level directories. All new code lives in `src/otb/` following the established
pattern.

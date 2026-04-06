# Implementation Plan: Export Book Annotations to Anki

**Branch**: `005-anki-cards-export` | **Date**: 2026-04-06 |
**Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-anki-cards-export/spec.md`

**Note**: Prose lines MUST wrap at 80 characters (Constitution Principle VII).

## Summary

Add an `otb anki export` command (and matching MCP tool) that reads book
annotations from a markdown annotation directory, then pushes them to an Anki
deck via AnkiConnect (the standard local REST add-on). Each annotation becomes
one "Basic" card: front = chapter + title, back = full text. On success, the
Anki note ID is written back to the annotation's markdown file as `anki_id`
in the frontmatter. Subsequent runs skip annotations whose `anki_id` note
still exists in Anki; stale IDs (note deleted) trigger re-creation.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `click`, `mcp` (FastMCP) — already installed;
`urllib.request` from stdlib for AnkiConnect HTTP calls (no new deps)
**Storage**: N/A (read-only from source; writes go to Anki via AnkiConnect)
**Testing**: pytest, fixtures in `tests/fixtures/`
**Target Platform**: local desktop (macOS/Linux, wherever Anki runs)
**Project Type**: CLI tool + MCP server
**Performance Goals**: 100 annotations exported in under 10 seconds
**Constraints**: AnkiConnect must be running; no new third-party dependencies
**Scale/Scope**: Single-user, local tool; batch size bounded by book size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                | Status | Notes                                |
| ------------------------ | ------ | ------------------------------------ |
| I. CLI-First             | PASS   | `otb anki export` added to Click     |
|                          |        | group                                |
| II. Shared Parser        | PASS   | Uses existing `Annotation`           |
|                          |        | dataclass and `parse_annotation_dir` |
| III. Test-First          | PASS   | Tests before implementation;         |
|                          |        | AnkiConnect calls mocked             |
| IV. Type Safety & Lint   | PASS   | mypy + pylint 10/10 enforced         |
| V. Simplicity / Min Deps | PASS   | `urllib.request`; no new packages    |
| VI. MCP Server           | PASS   | `anki_export` MCP tool delegates     |
|                          |        | to same service function as CLI      |
| VII. Document Formatting | PASS   | 80-char line wrap enforced           |

## Project Structure

### Documentation (this feature)

```text
specs/005-anki-cards-export/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   ├── cli.md           # CLI command contract
│   └── mcp-tool.md      # MCP tool contract
└── tasks.md             # Phase 2 output (/speckit.tasks — not yet created)
```

### Source Code

```text
src/otb/
├── anki.py              # NEW: AnkiConnect client + service function
├── cli.py               # MODIFIED: add `anki` group + `export` subcommand
├── mcp_server.py        # MODIFIED: add `anki_export` MCP tool
├── parser.py            # UNCHANGED
├── md_parser.py         # UNCHANGED
└── md_writer.py         # UNCHANGED

tests/
├── test_anki.py         # NEW: unit + integration tests for anki module
├── test_cli.py          # MODIFIED: add anki export CLI tests
├── test_mcp_server.py   # MODIFIED: add anki_export MCP tool tests
└── fixtures/            # UNCHANGED (existing HTML + md fixtures reused)
```

**Structure Decision**: Single-project layout (existing `src/otb/` package).
New logic is isolated in `src/otb/anki.py`. CLI and MCP layers delegate to
the service function in that module; no logic duplication.

## Phase 0: Research

Research complete. See [research.md](research.md).

All NEEDS CLARIFICATION items resolved:

| Question             | Decision                                          |
| -------------------- | ------------------------------------------------- |
| HTTP client          | `urllib.request` (stdlib, no new deps)            |
| Duplicate detection  | `anki_id`-first; `notesInfo` verifies stale IDs   |
| Input source         | markdown annotation directories only (no HTML)    |
| Card front format    | `{chapter} - {title}` or `{title}` if no chapter  |
| CLI placement        | `otb anki export` (new `anki` group)              |
| MCP tool             | `anki_export` delegating to `export_annotations`  |

## Phase 1: Design & Contracts

Design complete.

- [data-model.md](data-model.md) — entity mapping and validation rules
- [contracts/cli.md](contracts/cli.md) — CLI command schema and exit codes
- [contracts/mcp-tool.md](contracts/mcp-tool.md) — MCP tool schema
- [quickstart.md](quickstart.md) — user-facing setup and usage guide

### Key Design Decisions

**`src/otb/anki.py`** exposes:

1. `AnkiConnectError(Exception)` — raised when AnkiConnect returns a
   top-level error or is unreachable.

2. `AnkiClient` — thin wrapper:

   ```python
   class AnkiClient:
       def __init__(self, url: str = "http://localhost:8765") -> None: ...
       def create_deck(self, deck: str) -> None: ...
       def add_notes(self, notes: list[dict]) -> list[int | None]: ...
   ```

   Uses `urllib.request.urlopen` with a JSON body. Raises
   `AnkiConnectError` on connection failure or non-null `error` field.

3. `build_card(annotation, deck_name) -> dict` — pure function mapping an
   `Annotation` to an AnkiConnect note dict. Testable without network.

4. `export_annotations(annotations, deck, anki_url) -> ExportResult` —
   orchestrates deck creation, card building, and `addNotes` call.
   `ExportResult` is a `dataclass(frozen=True)` with `created`, `skipped`,
   `failed` integer fields.

**`src/otb/cli.py`** additions:

```python
@main.group()
def anki() -> None:
    """Commands for Anki flashcard export."""

@anki.command("export")
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--deck", default="", help="Target Anki deck name.")
@click.option("--anki-url", default="http://localhost:8765", ...)
def anki_export_cmd(path: Path, deck: str, anki_url: str) -> None: ...
```

**`src/otb/mcp_server.py`** additions:

```python
@mcp.tool(description="...")
def anki_export(
    path: str,
    deck: str = "",
    anki_url: str = "http://localhost:8765",
) -> dict[str, Any]: ...
```

### Test Strategy

**Unit tests** (no Anki running):

- `build_card`: covers chapter/no-chapter/empty-title cases.
- `AnkiClient._call`: mock `urllib.request.urlopen`; cover success, null
  results, and connection errors.
- `export_annotations`: mock `AnkiClient`; cover all-created, all-skipped,
  mixed, and blank-annotation cases.

**CLI integration tests** (mock `export_annotations`):

- Happy path with annotations directory fixture.
- `--deck` override.
- Anki unreachable → non-zero exit + stderr message.

**MCP tool tests** (mock `export_annotations`):

- Tool inputs and outputs conform to schema.
- `FileNotFoundError` and `AnkiConnectError` produce MCP error responses.

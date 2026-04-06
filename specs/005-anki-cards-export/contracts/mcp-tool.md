# MCP Tool Contract: `anki_export`

**Branch**: `005-anki-cards-export` | **Date**: 2026-04-06

## Tool Name

`anki_export`

## Description

Export book annotations from a Kindle HTML file or a directory of annotation
markdown files to an Anki deck via AnkiConnect. Returns a summary of created,
skipped, and failed cards.

## Input Schema

```python
anki_export(
    path: str,
    deck: str = "",
    anki_url: str = "http://localhost:8765",
) -> dict[str, Any]
```

| Parameter  | Type  | Req | Default             | Description        |
|------------|-------|-----|---------------------|--------------------|
| `path`     | `str` | Yes | --                  | Path to annotation |
|            |       |     |                     | markdown directory |
| `deck`     | `str` | No  | `""` (book title)   | Anki deck name.    |
|            |       |     |                     | Supports `Parent:` |
|            |       |     |                     | `::Child` syntax.  |
| `anki_url` | `str` | No  | `"http://localhost:` | AnkiConnect URL.  |
|            |       |     | `8765"`             |                    |

## Return Value

```json
{
  "created": 42,
  "skipped": 3,
  "failed": 0
}
```

| Field     | Type  | Description                                     |
|-----------|-------|-------------------------------------------------|
| `created` | `int` | Number of new Anki cards successfully created   |
| `skipped` | `int` | Duplicate cards and blank annotations skipped   |
| `failed`  | `int` | Cards that AnkiConnect failed to create         |

## Errors

The tool raises Python exceptions (FastMCP converts them to MCP error
responses):

| Exception             | When raised                                         |
|-----------------------|-----------------------------------------------------|
| `FileNotFoundError`   | `path` does not exist                               |
| `AnkiConnectError`    | Anki is unreachable or returns a top-level error    |
| `ValueError`          | No valid annotations found in the source            |

## Delegation

The MCP tool MUST delegate to the same `export_annotations` service
function used by the `otb anki export` CLI command. No logic duplication
between CLI and MCP layers (Constitution Principle VI).

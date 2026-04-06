# Data Model: Export Book Annotations to Anki

**Branch**: `005-anki-cards-export` | **Date**: 2026-04-06

## Existing Entities (unchanged)

### `Book`

Defined in `src/otb/parser.py`. No changes.

| Field    | Type  | Description                              |
|----------|-------|------------------------------------------|
| `title`  | `str` | Book title (used as default deck name)   |
| `author` | `str` | Author name (First Last format)          |

### `Annotation`

Defined in `src/otb/parser.py`. No changes.

| Field      | Type          | Description                               |
|------------|---------------|-------------------------------------------|
| `book`     | `Book`        | Parent book                               |
| `chapter`  | `str`         | Chapter heading (may be empty)            |
| `page`     | `int`         | Page number                               |
| `location` | `int`         | Kindle location                           |
| `text`     | `str`         | Full annotation text (card back)          |
| `title`    | `str`         | Auto-generated short title (card front)   |
| `color`    | `str \| None` | Highlight colour (unused in v1)           |
| `number`   | `int`         | Sequence number within the book           |

---

## New Entities (in `src/otb/anki.py`)

### `AnkiNote` (dict structure, not a dataclass)

Represents the JSON payload sent to AnkiConnect's `addNotes` action for a
single card.

| Key        | Type            | Description                               |
|------------|-----------------|-------------------------------------------|
| `deckName` | `str`           | Target Anki deck name                     |
| `modelName`| `str`           | Always `"Basic"` in v1                    |
| `fields`   | `dict[str, str]`| `{"Front": "...", "Back": "..."}`         |
| `options`  | `dict[str, Any]`| `{"allowDuplicate": false}`               |

### `ExportResult` (returned by `export_annotations`)

| Field     | Type  | Description                        |
|-----------|-------|------------------------------------|
| `created` | `int` | Number of new cards added to Anki  |
| `skipped` | `int` | Duplicates and blank annotations   |
| `failed`  | `int` | API errors for individual notes    |

---

## Card Content Mapping

| Card Field | Source                                                |
| ---------- | ----------------------------------------------------- |
| **Front**  | `"{chapter} - {title}"` when chapter is non-empty     |
|            | `"{title}"` when chapter is empty                     |
|            | First 60 chars of `text` (truncated) if title empty   |
| **Back**   | `annotation.text` (full, unmodified)                  |

---

## Validation Rules

- Annotations with empty or whitespace-only `text` are skipped before any
  Anki call is made.
- If the parsed source yields zero valid annotations, the command exits
  with a user-facing message (no Anki connection is attempted).
- The `modelName` `"Basic"` is assumed present in the user's Anki
  collection. The command does not create or modify note types.

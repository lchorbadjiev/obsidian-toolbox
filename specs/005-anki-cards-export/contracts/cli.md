# CLI Contract: `otb anki export`

**Branch**: `005-anki-cards-export` | **Date**: 2026-04-06

## Command

```
otb anki export [OPTIONS] PATH
```

## Arguments

| Argument | Type        | Required | Description                              |
|----------|-------------|----------|------------------------------------------|
| `PATH`   | `click.Path`| Yes      | Path to a Kindle HTML file or to a       |
|          |             |          | directory of annotation markdown files.  |
|          |             |          | Must exist. Both files and directories   |
|          |             |          | are accepted.                            |

## Options

| Option       | Type  | Default                       | Description                   |
|--------------|-------|-------------------------------|-------------------------------|
| `--deck`     | `str` | Book title from first         | Target Anki deck name.        |
|              |       | annotation                    | Supports nested decks via     |
|              |       |                               | `Parent::Child` syntax.       |
| `--anki-url` | `str` | `http://localhost:8765`       | Base URL for AnkiConnect.     |

## Exit Codes

| Code | Meaning                                              |
|------|------------------------------------------------------|
| `0`  | All annotations processed (some may be skipped)      |
| `1`  | Fatal error: Anki unreachable, path invalid, or no   |
|      | annotations found                                    |

## Standard Output

On success, the command writes a single summary line to stdout:

```
Created: 42  Skipped: 3  Failed: 0
```

## Standard Error

All errors and warnings are written to stderr. Examples:

```
Error: Cannot connect to Anki at http://localhost:8765.
       Make sure Anki is running with the AnkiConnect add-on installed.

Error: No annotations found in <path>.

Warning: Skipped 2 annotation(s) with empty text.
```

## Examples

```bash
# Export from a Kindle HTML file (deck name = book title)
otb anki export ~/exports/my_book.html

# Export from a markdown annotations directory
otb anki export ~/annotations/my_book/

# Send to a custom deck
otb anki export ~/exports/my_book.html --deck "Books::Non-Fiction"

# Use a non-default AnkiConnect port
otb anki export ~/exports/my_book.html --anki-url http://localhost:8080
```

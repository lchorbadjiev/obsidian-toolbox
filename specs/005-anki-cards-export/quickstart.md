# Quickstart: Export Book Annotations to Anki

**Branch**: `005-anki-cards-export`

## Prerequisites

1. Anki desktop app is installed and open.
2. The AnkiConnect add-on (ID `2055492823`) is installed in Anki.
   Install via: Anki → Tools → Add-ons → Get Add-ons → paste ID.
3. `obsidian-toolbox` is installed: `uv sync`

## Export from a Kindle HTML file

```bash
# Download your Kindle notebook from the Kindle app and export as HTML.
otb anki export ~/Downloads/my_book_notes.html
# Output: Created: 37  Skipped: 0  Failed: 0
```

## Export from a markdown annotations directory

```bash
otb anki export ~/obsidian/annotations/My\ Book/
# Output: Created: 37  Skipped: 0  Failed: 0
```

## Use a custom deck name

```bash
# Supports Anki nested deck syntax
otb anki export ~/Downloads/my_book_notes.html --deck "Books::Non-Fiction"
```

## Re-run safely (idempotent)

Running the command again on the same source skips existing cards:

```bash
otb anki export ~/Downloads/my_book_notes.html
# Output: Created: 0  Skipped: 37  Failed: 0
```

## Non-default AnkiConnect port

```bash
otb anki export ~/Downloads/my_book_notes.html --anki-url http://localhost:8080
```

## Troubleshooting

**"Cannot connect to Anki"** — Make sure Anki is open. Restart Anki if the
add-on was just installed.

**"No annotations found"** — Check the path points to a valid `.html` file
or a directory containing `.md` annotation files.

**Some cards show "Failed"** — The "Basic" note type must exist in your
Anki collection. Open Anki and verify via Tools → Manage Note Types.

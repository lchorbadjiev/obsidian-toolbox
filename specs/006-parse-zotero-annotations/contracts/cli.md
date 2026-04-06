# CLI Contract: Zotero Commands

**Feature**: 006-parse-zotero-annotations
**Date**: 2026-04-06

## Command: `otb zotero parse`

```text
Usage: otb zotero parse [OPTIONS] INPUT_DIR OUTPUT_DIR

  Parse Zotero annotations and write individual markdown files.

Arguments:
  INPUT_DIR   Directory containing Annotations.md and book.txt
  OUTPUT_DIR  Directory to write annotation markdown files

Options:
  --help  Show this message and exit.
```

### Behavior

- Reads `INPUT_DIR/book.txt` for book metadata.
- Reads `INPUT_DIR/Annotations.md` for annotation text.
- Writes one `.md` file per annotation to `OUTPUT_DIR`.
- Prints the number of annotations written to stdout.
- Exits with code 0 on success.
- Exits with code 1 if `book.txt` or `Annotations.md` is
  missing, printing error to stderr.

### Output Format

Each annotation file follows the standard format:

```markdown
---
source: "Book Title"
author: Author Name
chapter: ""
page: 42
location: 42
type: annotation
number: 1
---

# Auto Generated Title Here

> The annotation text as a blockquote
```

### Exit Codes

| Code | Meaning                             |
|------|-------------------------------------|
| 0    | Success                             |
| 1    | Missing input files or parse error  |

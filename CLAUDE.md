# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code)
when working with code in this repository.

## Commands

```bash
uv sync                        # install / update dependencies
uv run otb                     # run the CLI
uv run pytest                  # run all tests
uv run pytest tests/test_X.py  # run a single test file
uv run mypy src/ tests/        # type-check
uv run pylint src/ tests/      # lint (target: 10/10)
pymarkdownlnt scan -r --respect-gitignore .        # markdown lint (zero errors)
pymarkdownlnt fix -r --respect-gitignore .         # autofix easy formatting issues
```

## Architecture

`src/otb/` — package root using a `src` layout.
`src/otb/cli.py:main` — Click CLI entrypoint
(`@click.group()`), registered as the `otb` script
in `pyproject.toml`.

### Parsers

Both parsers produce `list[Annotation]` using shared
dataclasses defined in `parser.py`.

- **`parser.py`** — parses Kindle notebook HTML exports
  (`parse_notebook`). Defines `Book` and `Annotation`
  dataclasses shared across all parsers. Author names
  are normalized from "Last, First" to "First Last".
- **`md_parser.py`** — parses annotation markdown files
  with YAML-like frontmatter (`parse_annotation_md`,
  `parse_annotation_dir`). Uses regex only;
  no yaml dependency.

### Dataclasses (`parser.py`)

```python
Book(title, author)
Annotation(book, chapter, page, location, text, title="", color=None)
```

`color` is `str | None` — present from HTML parser,
always `None` from markdown parser.
`title` is auto-generated from the first sentence
(up to 7 words, title-cased).

### Tests

Fixtures live in `tests/fixtures/`: one HTML file and
`tests/fixtures/annotations/` for markdown files.
All test files suppress `missing-function-docstring`
with a file-level pylint comment;
`redefined-outer-name` is suppressed globally in
`pyproject.toml` for the pytest fixture pattern.

--- BEGIN AGENTS.MD CONTENT ---

## Issue Tracking with br (beads_rust)

**Note:** `br` is non-invasive and never executes git
commands. After `br sync --flush-only`, you must
manually run `git add .beads/ && git commit`.

**Quick reference:**

- `br ready` - Find unblocked work
- `br create "Title" --type task --priority 2` -
  Create issue
- `br close <id>` - Complete work
- Sync and push:

  ```bash
  br sync --flush-only
  git add .beads/
  git commit -m "sync beads"
  git push
  ```

--- END AGENTS.MD CONTENT ---

## Active Technologies

- Python 3.12+ + mcp (FastMCP), click, beautifulsoup4 (009-kindle-import-file-passing)
- Filesystem (temp JSON files, markdown output) (009-kindle-import-file-passing)
- Python 3.12+ + None new — uses existing `click`, `mcp` (010-boox-parser)
- Filesystem (reads Boox export dirs, writes markdown) (010-boox-parser)

- Python 3.12+ + mcp (FastMCP) — no new deps
  (008-kindle-import-prompt)
- Python 3.12+ + all existing (`click`,
  `beautifulsoup4`, `mcp`) — no new deps
  (002-parse-md-highlights)
- N/A (read-only; no files written)
  (002-parse-md-highlights)
- Python 3.12+ + `mcp` (FastMCP) — already
  installed; `click` — already installed
  (003-book-index-prompt)
- Python 3.12+ + `click`, `mcp` (FastMCP) —
  already installed; (005-anki-cards-export)
- N/A (read-only from source; writes go to Anki
  via AnkiConnect) (005-anki-cards-export)
- Python 3.12+ + click, mcp (FastMCP) -- already
  (006-parse-zotero-annotations)
- Filesystem (reads Zotero exports, writes markdown
  (006-parse-zotero-annotations))
- Python 3.12+ + click, mcp (FastMCP) + aspell
  (system command-line tool,
  (007-fix-zotero-word-concat))

## Recent Changes

- 002-parse-md-highlights: Added Python 3.12+ +
  all existing (`click`, `beautifulsoup4`, `mcp`)
  — no new deps

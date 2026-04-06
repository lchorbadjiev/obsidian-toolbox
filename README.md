# Obsidian Toolbox

A CLI tool and MCP server for converting Kindle notebook exports into
Obsidian-ready markdown annotation files, book index documents, and
Anki flashcard decks.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo>
cd obsidian-toolbox
uv sync
```

This installs the `otb` CLI command.

## MCP Server Setup in Claude Code

Add the server to your Claude Code MCP configuration:

```bash
claude mcp add obsidian-toolbox -- uv --directory /path/to/obsidian-toolbox run otb mcp
```

Replace `/path/to/obsidian-toolbox` with the absolute path to this
repository on your machine.

Verify the server is registered:

```bash
claude mcp list
```

Once added, Claude Code will start the server automatically when you
open a project. The following tools and prompts become available to
the agent:

| Name | Type | Description |
|------|------|-------------|
| `parse_kindle_export` | tool | Parse a Kindle HTML export into annotations |
| `save_annotations` | tool | Save annotations as individual `.md` files |
| `parse_md_annotations_dir` | tool | Read a directory of annotation `.md` files |
| `anki_export` | tool | Export annotation `.md` files to an Anki deck |
| `generate_book_index` | prompt | Generate a book index from an annotations dir |

## Workflow: Kindle Export → Markdown Annotations → Book Index

### Step 1 — Export from Kindle

In the Kindle app, open your annotations for a book and export them as
an HTML file (e.g. `A Brief History of Time - Notebook.html`).

### Step 2 — Parse and save annotations

Ask Claude (with the MCP server active):

> Parse the Kindle export at `~/Downloads/A Brief History of Time - Notebook.html`,
> generate a short title for each annotation, then save them to
> `~/notes/a-brief-history/notes/`.

Claude will:
1. Call `parse_kindle_export` to read the HTML file.
2. Generate a concise title (under 10 words) for each annotation.
3. Call `save_annotations` to write one `.md` file per annotation.

Each output file follows this format:

```markdown
---
source: "A Brief History of Time"
author: Stephen Hawking
chapter: "1   Our Picture of the Universe"
page: 1
location: 42
type: annotation
number: 1
---

# A Well-Known Scientist Once Gave a Public Lecture on Astronomy

> A well-known scientist once gave a public lecture on astronomy.

**Citation:** Hawking, Stephen. *A Brief History of Time*. ...
```

Files are named `001 - Title of Annotation.md`, `002 - ...`, etc.

### Step 3 — Generate the book index

Ask Claude:

> Using the `generate_book_index` prompt with
> `~/notes/a-brief-history/notes/`, create the book index and save it
> as `~/notes/a-brief-history/A Brief History of Time - Index.md`.

Claude will:
1. Call the `generate_book_index` prompt, which reads all annotation
   files and returns structured context.
2. Write a prose summary of the book.
3. Save the index file.

The resulting index looks like:

```markdown
---
tags: [book, cosmology]
author: Stephen Hawking
published: 1988
---

# A Brief History of Time

Stephen Hawking's landmark work explains the nature of space, time,
and the universe for a general audience...

---

## Notes by Chapter

### 1   Our Picture of the Universe
- [[notes/001 - A Well-Known Scientist Once Gave a Public Lecture on Astronomy]]
- [[notes/002 - Any Physical Theory Is Always Provisional]]
...
```

All wikilinks point to the individual annotation files, making the
index fully navigable in Obsidian.

## Workflow: Annotation Files → Anki Flashcards

### Prerequisites

1. Anki desktop app is open.
2. The [AnkiConnect](https://ankiweb.net/shared/info/2055492823) add-on
   is installed (add-on ID `2055492823`).

### Export to Anki

Run the command pointing at a directory of annotation markdown files:

```bash
otb anki export ~/notes/a-brief-history/notes/
```

Each annotation becomes one **Basic** card:

- **Front**: chapter name + annotation title
- **Back**: full annotation text

The target deck is named after the book title by default. On success,
each markdown file is updated with an `anki_id` frontmatter field
containing the Anki note ID, so re-running the command skips
already-exported annotations.

```bash
# Send to a custom or nested deck
otb anki export ~/notes/a-brief-history/notes/ --deck "Books::Non-Fiction"

# Use a non-default AnkiConnect port
otb anki export ~/notes/a-brief-history/notes/ --anki-url http://localhost:8080
```

Output:

```
Created: 42  Skipped: 0  Failed: 0
```

Re-running after adding new annotations only exports the new ones:

```
Created: 3  Skipped: 42  Failed: 0
```

## CLI Reference

```bash
# Count annotations in a Kindle export
otb kindle count path/to/export.html

# Count annotations in a directory of .md files
otb md count path/to/notes/

# Print the book index generation prompt (inspect or pipe)
otb md index-prompt path/to/notes/

# Export annotation .md files to an Anki deck
otb anki export path/to/notes/
otb anki export path/to/notes/ --deck "Books::Non-Fiction"
otb anki export path/to/notes/ --anki-url http://localhost:8080

# Start the MCP server manually (stdio transport)
otb mcp
```

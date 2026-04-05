# Obsidian Toolbox

A CLI tool and MCP server for converting Kindle notebook exports into
Obsidian-ready markdown annotation files and book index documents.

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
| `save_highlights` | tool | Save annotations as individual `.md` files |
| `parse_md_highlights_dir` | tool | Read a directory of annotation `.md` files |
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
3. Call `save_highlights` to write one `.md` file per annotation.

Each output file follows this format:

```markdown
---
source: "A Brief History of Time"
author: Stephen Hawking
chapter: "1   Our Picture of the Universe"
page: 1
location: 42
type: highlight
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

## CLI Reference

```bash
# Count annotations in a Kindle export
otb kindle count path/to/export.html

# Count annotations in a directory of .md files
otb md count path/to/notes/

# Print the book index generation prompt (inspect or pipe)
otb md index-prompt path/to/notes/

# Start the MCP server manually (stdio transport)
otb mcp
```

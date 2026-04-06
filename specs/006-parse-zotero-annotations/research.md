# Research: Parse Zotero Annotations

**Feature**: 006-parse-zotero-annotations
**Date**: 2026-04-06

## R1: Zotero Annotation Export Format

**Decision**: Parse the Zotero markdown export format using regex.

**Rationale**: The Zotero export is a simple markdown file where
each annotation is a double-quoted string followed by a parenthetical
citation `("BookTitle", p. XX)`. Blank lines separate annotations.
The file header contains `# Annotations` and a timestamp line.
Regex is sufficient and consistent with the existing `md_parser.py`
approach (Constitution Principle V: Simplicity).

**Format observed in fixture**:

```text
# Annotations
(3/26/2026, 5:55:13 PM)

"Quoted annotation text here" ("Book Title", p. 42)

"Another annotation" ("Book Title", p. 43)
```

**Alternatives considered**:

- YAML/JSON parser: Not applicable -- format is not YAML/JSON.
- Markdown AST parser (e.g., `mistune`): Overkill for this
  format and would add a dependency. Regex is simpler.

## R2: Book Metadata Format (book.txt)

**Decision**: Parse `book.txt` as alternating label/value lines.

**Rationale**: The file uses a two-line-per-field format where
the field label is on one line and its value on the next:

```text
Title
Refactoring: Improving the Design of Existing Code
Authors
Martin Fowler
```

Only `Title` and `Authors` fields are needed. The `Author sort`
field (`Fowler, Martin`) exists but the `Authors` field already
has the display-ready format (`Martin Fowler`), so no "Last,
First" normalization is needed for Zotero (unlike Kindle).

**Alternatives considered**:

- Parse all fields: Unnecessary -- only title and author are
  used in the `Book` dataclass.
- Use `Author sort` with normalization: `Authors` field already
  has the correct format.

## R3: Existing Writer Reuse

**Decision**: Reuse `md_writer.py` for writing annotation files.

**Rationale**: `write_annotations()` already handles the full
workflow: rendering frontmatter + title + blockquote, sanitizing
filenames, numbering, and creating directories. The `_render()`
function produces exactly the format needed. No citation line
is included by the writer (citations in fixture files were
added manually), which aligns with the clarification to mirror
Kindle format omitting unavailable fields.

**Alternatives considered**:

- Custom Zotero writer: Would duplicate logic and violate
  Constitution Principle II (Shared Parser Contract).

## R4: CLI Command Structure

**Decision**: Add a `zotero` command group with a `parse`
subcommand: `otb zotero parse <input-dir> <output-dir>`.

**Rationale**: Follows the existing pattern (`otb kindle count`,
`otb md count`, `otb anki export`). The command takes the Zotero
export directory as input and an output directory for the
annotation markdown files.

**Alternatives considered**:

- Single top-level command (`otb parse-zotero`): Inconsistent
  with the existing group-based CLI structure.
- Separate commands for parse and write: Over-engineering for
  a single workflow.

## R5: MCP Tool

**Decision**: Add a `parse_zotero_export` MCP tool that mirrors
the CLI capability.

**Rationale**: Constitution Principle VI requires every CLI
capability to also be an MCP tool. The tool delegates to the
same parser function.

**Alternatives considered**: None -- this is a constitution
requirement.

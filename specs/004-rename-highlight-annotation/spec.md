# Feature Specification: Rename Highlight to Annotation

**Feature Branch**: `004-rename-highlight-annotation`
**Created**: 2026-04-05
**Status**: Draft
**Input**: User description: "Now we use Highlight for the notes we
create from Kindle and markdown directory. The better term is
Annotation. From the Kindle app we export annotations. We should
switch to using annotation instead of highlight."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consistent Annotation Terminology (Priority: P1)

A user interacts with the tool through its CLI commands, MCP tools,
MCP prompts, and saved markdown files. Every surface they touch — help
text, tool names, file content, and code identifiers — uses the word
"annotation" rather than "highlight", matching the language Kindle
itself uses when exporting from the app.

**Why this priority**: This is the entire scope of the feature. All
terminology changes are part of one cohesive rename; there is no
meaningful subset to deliver first.

**Independent Test**: Run `otb --help` and all subcommand help pages;
verify no user-visible text contains "highlight". Inspect an
annotation file saved by the tool; verify the `type` frontmatter field
reads `annotation`. Verify MCP tool and prompt names no longer contain
"highlight". Verify all internal code identifiers (classes, functions,
variables) have been renamed to match.

**Acceptance Scenarios**:

1. **Given** a user reads CLI help text, **When** they view any
   command's description, **Then** the word "highlight" does not
   appear in any user-visible output.

2. **Given** the tool saves an annotation to disk, **When** the user
   opens the file, **Then** the frontmatter `type` field reads
   `annotation`, not `highlight`.

3. **Given** an existing file with `type: highlight` in its
   frontmatter, **When** the tool parses that file, **Then** it is
   read successfully without error (backward compatibility preserved).

4. **Given** an AI agent uses the MCP server, **When** it lists
   available tools and prompts, **Then** all names and descriptions
   use "annotation" instead of "highlight".

5. **Given** a developer reads the source code, **When** they inspect
   any class, function, or variable name, **Then** names use
   "annotation" consistently (e.g. `Annotation`, `parse_annotation_md`,
   `save_annotations`).

---

### Edge Cases

- Existing `.md` files with `type: highlight` must still parse
  without error after this change.
- Test fixtures and test helper names must also be updated to avoid
  confusion.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: All CLI command help text MUST use "annotation" instead
  of "highlight" in any user-visible description or output.

- **FR-002**: The `type` field written to frontmatter of saved
  annotation files MUST read `annotation`.

- **FR-003**: The parser MUST accept both `type: annotation` and
  `type: highlight` in frontmatter to preserve backward compatibility
  with files created before this change.

- **FR-004**: All MCP tool names, prompt names, and their
  descriptions MUST use "annotation" terminology (e.g.
  `save_annotations`, `parse_md_annotations_dir`).

- **FR-005**: All internal code identifiers — class names, function
  names, variable names, and parameter names — MUST be renamed to use
  "annotation" (e.g. `Annotation`, `parse_annotation_md`,
  `parse_annotation_dir`, `write_annotations`).

- **FR-006**: All test names, fixture references, and test helper
  identifiers MUST be updated to use "annotation" terminology.

- **FR-007**: No regression: every capability that worked before the
  rename MUST continue to work identically after it.

### Key Entities

- **Annotation**: The renamed form of what was previously called
  "Highlight" — a single extracted passage from a book, with
  associated metadata (book title, author, chapter, page, location,
  text, title, color, number).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A full-text search of all source files, test files,
  and documentation for the word "highlight" (case-insensitive)
  returns zero results in user-visible strings, identifiers, and
  comments — except where retained intentionally for backward
  compatibility (the `type: highlight` parser fallback).

- **SC-002**: All existing tests pass without modification to their
  assertions after the rename (behavior is identical, only names
  change).

- **SC-003**: A file saved by the tool after this change opens and
  round-trips correctly — it can be read back by the parser and
  produces the same data as before.

## Assumptions

- The MCP tool `save_highlights` is renamed to `save_annotations`;
  any existing agent integrations that call `save_highlights` by name
  will need to update their tool calls (no runtime alias provided).
- The `type: highlight` frontmatter value in existing files is treated
  as equivalent to `type: annotation` during parsing; no migration
  script is provided.
- The rename covers all files under `src/`, `tests/`, `specs/`, and
  `CLAUDE.md`; external documentation (e.g. git history, commit
  messages) is not rewritten.

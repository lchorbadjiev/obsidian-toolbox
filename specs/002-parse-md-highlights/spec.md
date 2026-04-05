# Feature Specification: Parse MD Highlights MCP Tool

**Feature Branch**: `002-parse-md-highlights`
**Created**: 2026-04-05
**Status**: Draft
**Input**: User description: "Now we need a parser for a directory of MD highlights. the MCP server should be able to expose this directory as a list of Highlights."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a Highlights Directory via MCP (Priority: P1)

An LLM agent provides the path to a directory containing highlight markdown files and
receives a structured list of all highlights found in that directory. The agent can
then process, filter, or display those highlights without needing to read individual
files itself.

**Why this priority**: This is the entire feature — a single, self-contained capability
with immediate value. Reading a highlights directory is the symmetric counterpart to
saving one, completing the parse → title → save → re-read workflow.

**Independent Test**: Can be fully tested by calling the tool with the path to the
existing markdown fixtures directory and verifying a non-empty list of highlights is
returned with correct book metadata, chapter, page, location, and text for each file.

**Acceptance Scenarios**:

1. **Given** a directory containing one or more highlight markdown files, **When** the
   tool is called with that path, **Then** a list of highlights is returned, one per
   file, each containing: book title, author, chapter, page, location, text, title
   (if present in the file), color (if present), and number.
2. **Given** a directory where files are named with a numeric prefix (e.g. `001 - ...`,
   `002 - ...`), **When** the tool is called, **Then** highlights are returned in
   filename-sorted order.
3. **Given** a directory that exists but contains no `.md` files, **When** the tool is
   called, **Then** an empty list is returned (not an error).
4. **Given** a path to a directory that does not exist, **When** the tool is called,
   **Then** a descriptive error is returned.
5. **Given** a path to a file (not a directory), **When** the tool is called,
   **Then** a descriptive error is returned.

---

### Edge Cases

- What happens when a `.md` file in the directory is malformed (missing frontmatter or
  blockquote)? That file is skipped and the error is reported alongside the successfully
  parsed highlights.
- What happens when the directory contains non-`.md` files? They are silently ignored.
- What happens when a highlight file has no title heading? It is returned with an empty
  title field (consistent with the existing parser behaviour for title-less files).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The MCP server MUST expose a tool that accepts a directory path and
  returns a structured list of all highlights found in `.md` files within that
  directory.
- **FR-002**: Highlights MUST be returned in filename-sorted order.
- **FR-003**: Each returned highlight MUST include: book title, author, chapter, page,
  location, text, title (empty string if absent), color (null if absent), and number.
- **FR-004**: An empty directory MUST return an empty list, not an error.
- **FR-005**: A non-existent path or a path to a file (not a directory) MUST return a
  descriptive error.
- **FR-006**: Malformed files MUST NOT cause the entire call to fail; successfully
  parsed highlights MUST be returned alongside an indication of which files could not
  be parsed.

### Key Entities

- **Highlight**: Same shared data structure used across all parsers — book (title,
  author), chapter, page, location, text, title (optional), color (optional), number.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An LLM agent can read a directory of 100+ highlight files and receive the
  full list in a single tool call within 5 seconds.
- **SC-002**: Highlights returned by the tool are byte-for-byte equivalent in content
  to those produced by the existing single-file markdown highlight parser applied to
  the same files individually.
- **SC-003**: The tool is accessible from any MCP-compatible client without additional
  configuration beyond what is already required to run the existing MCP server.

## Assumptions

- The directory contains only highlight markdown files in the format produced by the
  existing save-highlights tool (YAML-like frontmatter + optional H1 + blockquote).
- Subdirectories within the target path are not recursed into; only `.md` files
  directly inside the given directory are parsed.
- The feature reuses the existing single-file markdown highlight parser; no new parsing
  logic is introduced.
- The MCP server is already running (this feature adds one tool to the existing server,
  not a new server).

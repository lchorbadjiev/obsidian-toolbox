# Feature Specification: Improve Kindle Import MCP Tools

**Feature Branch**: `009-kindle-import-file-passing`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "Improve Kindle Import MCP Tools -
file-path-based data passing to avoid token explosion"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse Large Kindle Export Without Token Overflow (Priority: P1)

A user has a Kindle HTML export with 100+ annotations. They
invoke the `parse_kindle_export` tool via the MCP prompt. The
tool parses the file, writes all annotations to a temporary
JSON file, and returns a lightweight summary (file path, count,
book title, chapter list) instead of the full annotation array.
The user never sees the raw 100K+ character payload in their
conversation context.

**Why this priority**: This is the root cause of the workflow
breakdown. Without this change, large exports exceed the LLM
context window and the entire import fails or requires manual
workarounds.

**Independent Test**: Can be tested by calling
`parse_kindle_export` on a large HTML file and verifying the
response contains only a summary (path, count, metadata) while
the full data exists in the referenced temp file.

**Acceptance Scenarios**:

1. **Given** a Kindle HTML export with 166 annotations,
   **When** the user calls `parse_kindle_export(path=X)`,
   **Then** the tool writes a JSON file containing all 166
   annotations and returns a summary with the file path,
   annotation count, book title, and chapter list.
2. **Given** a Kindle HTML export with 5 annotations,
   **When** the user calls `parse_kindle_export(path=X)`,
   **Then** the tool still writes to a temp file and returns
   a summary, maintaining a consistent interface regardless
   of annotation count.
3. **Given** a non-existent file path,
   **When** the user calls `parse_kindle_export(path=X)`,
   **Then** the tool returns a clear error message indicating
   the file was not found.

---

### User Story 2 - Save Annotations From File Path (Priority: P2)

After generating titles for annotations (stored in the temp
JSON file), the user calls `save_annotations` with just the
file path instead of passing the full annotation array through
the LLM context. The tool reads the JSON file and writes all
annotation markdown files in a single call.

**Why this priority**: Without this, saving 166 annotations
requires 6+ batched calls because the annotation array is too
large to serialize through the LLM context. This change makes
saving a single-call operation.

**Independent Test**: Can be tested by providing a JSON file
path containing annotations with titles and verifying all
markdown files are written correctly.

**Acceptance Scenarios**:

1. **Given** a JSON file containing 166 annotations with
   titles, **When** the user calls
   `save_annotations(file_path=X, directory=Y)`,
   **Then** all 166 markdown files are written to directory Y.
2. **Given** the `save_annotations` tool, **When** the user
   passes the `annotations` parameter directly (existing
   behavior), **Then** the tool works as before, maintaining
   backward compatibility.
3. **Given** a JSON file path that does not exist,
   **When** the user calls `save_annotations(file_path=X)`,
   **Then** the tool returns a clear error message.

---

### User Story 3 - End-to-End Import With Title Generation (Priority: P3)

A user triggers the full Kindle import workflow via the MCP
prompt. The prompt orchestrates three steps: (1) parse to temp
file, (2) generate titles in batches of ~30 annotations using
LLM subagents reading/writing the temp file, (3) save all
annotations from the temp file. The user only interacts with
the high-level workflow; data flows through the file system
rather than the conversation context.

**Why this priority**: This is the integration of Stories 1 and
2 with the title-generation step. It depends on both previous
stories being complete.

**Independent Test**: Can be tested end-to-end by providing a
Kindle HTML export and verifying that all annotations are saved
as markdown files with LLM-generated titles.

**Acceptance Scenarios**:

1. **Given** a Kindle HTML export with 166 annotations,
   **When** the user triggers the import workflow,
   **Then** the system parses to a temp file, generates titles
   in batches of ~30, and saves all files in a total of
   3 tool calls (parse, title-gen, save) rather than 7+.
2. **Given** a Kindle HTML export, **When** the title
   generation step runs, **Then** each batch contains
   approximately 30 annotations to balance quality and
   parallelism.

---

### Edge Cases

- What happens when the temp JSON file is modified or deleted
  between parse and save steps?
- How does the system handle annotations with special
  characters or very long text in JSON serialization?
- What happens if title generation partially fails (some
  batches succeed, others fail)? → Annotations are saved
  without a title (empty title field).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The parse tool MUST write all parsed annotations
  to a temporary JSON file rather than returning them inline.
- **FR-002**: The parse tool MUST return a summary containing:
  the temp file path, total annotation count, book title, and
  list of chapters found.
- **FR-003**: The save tool MUST accept a `file_path` parameter
  as an alternative to the existing `annotations` parameter.
- **FR-004**: The save tool MUST maintain backward compatibility
  with the existing `annotations` parameter for callers that
  pass annotation data directly.
- **FR-005**: When `file_path` is provided, the save tool MUST
  read annotations from the specified JSON file and write them
  as individual markdown files.
- **FR-010**: The save tool MUST return an error if both
  `file_path` and `annotations` are provided — the caller
  must supply exactly one.
- **FR-006**: The MCP prompt MUST instruct the caller to use
  file-path-based data passing for all steps.
- **FR-007**: The MCP prompt MUST recommend batches of ~30
  annotations per subagent for title generation.
- **FR-008**: The temp JSON file MUST use the same annotation
  schema as the existing inline format (book_title, author,
  chapter, page, location, text, color, number, title).
- **FR-009**: The parse tool MUST handle the same input formats
  and produce the same annotation data as the current
  implementation — only the delivery mechanism changes.

### Key Entities

- **Annotation**: A highlighted passage from a Kindle book,
  with metadata (book, chapter, page, location, text, color)
  and a generated title. Stored as JSON in the temp file and
  as individual markdown files in the output directory.
- **Temp Annotations File**: A JSON file written by the parse
  tool and consumed by the save tool. Contains the full array
  of annotation objects. Serves as the data-passing mechanism
  between tools.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A 166-annotation Kindle import completes with
  exactly 2 MCP tool calls for data handling (1 parse, 1 save)
  instead of 7+ calls.
- **SC-002**: The parse tool response fits within a single
  short message (under 500 characters) regardless of how many
  annotations the export contains.
- **SC-003**: All annotations from the source HTML file are
  preserved in the output markdown files with no data loss.
- **SC-004**: Existing callers using the `annotations`
  parameter directly continue to work without modification.

## Clarifications

### Session 2026-04-06

- Q: What should happen if both `file_path` and `annotations`
  are provided to `save_annotations`? → A: Return an error —
  caller must provide exactly one.
- Q: How should the workflow handle annotations where title
  generation fails? → A: Save the annotation without a title
  (empty title field).

## Assumptions

- The temp file is written to a system temp directory and
  persists for the duration of the import session (typically
  under 10 minutes).
- Title generation remains an LLM responsibility and is not
  moved into the MCP server.
- The JSON schema for annotations in the temp file matches
  the existing dict format used by the inline `annotations`
  parameter.
- The MCP prompt is the primary orchestrator of the import
  workflow; the tools themselves do not chain automatically.

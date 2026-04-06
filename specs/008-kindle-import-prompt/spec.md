# Feature Specification: Kindle Import Annotations Prompt

**Feature Branch**: `008-kindle-import-prompt`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "I want to have an MCP prompt
that imports a file with Kindle annotations using the
following workflow: first parse the Kindle annotations file
using the parse_kindle_export tool, then using a subagent
running haiku generates a title for each annotation, and
at the end saves all annotations using save_annotations
tool. The prompt should be named
/kindle-import-annotations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Import Kindle Annotations (Priority: P1)

As an MCP client user, I want to invoke a single prompt
called `/kindle-import-annotations` that orchestrates the
full workflow of parsing a Kindle HTML export, generating
titles for each annotation, and saving them as individual
markdown files — so I can import a book's annotations in
one step without manually coordinating multiple tool calls.

**Why this priority**: This is the entire feature — a
single orchestrated prompt that replaces three manual steps
(parse, title, save) with one invocation.

**Independent Test**: Call the
`/kindle-import-annotations` prompt with a path to a
Kindle HTML export and an output directory. Verify that
the output directory contains one markdown file per
annotation, each with a meaningful title.

**Acceptance Scenarios**:

1. **Given** a Kindle HTML export file, **When** the user
   invokes the `/kindle-import-annotations` prompt with
   just the file path, **Then** the system parses all
   annotations and saves output to a `notes/`
   subdirectory alongside the export file.
2. **Given** parsed annotations with empty titles,
   **When** the prompt workflow runs, **Then** a
   lightweight AI model generates a concise title (under
   10 words) for each annotation based on its text.
3. **Given** annotations with generated titles, **When**
   the workflow completes, **Then** all annotations are
   saved as individual markdown files in the specified
   output directory.
4. **Given** a successful import, **When** the user
   checks the output, **Then** each file has correct
   frontmatter (source, author, chapter, page, location,
   number) and a blockquote with the annotation text.

---

### User Story 2 — Error Reporting (Priority: P2)

As a user, I want clear error messages when the import
fails so I can fix the issue and retry.

**Why this priority**: Without clear errors, users cannot
diagnose problems with their input files or paths.

**Independent Test**: Invoke the prompt with an invalid
file path and verify that a clear, actionable error
message is returned.

**Acceptance Scenarios**:

1. **Given** a non-existent file path, **When** the user
   invokes the prompt, **Then** the system returns an
   error message indicating the file was not found.
2. **Given** a valid file but an invalid output directory
   (e.g., a path pointing to a file), **When** the
   prompt runs, **Then** the system returns an error
   before attempting to write files.

---

### Edge Cases

- What happens when the Kindle export contains zero
  annotations? The prompt should complete successfully
  and report that no annotations were found.
- What happens when the title generation step fails for
  some annotations? The system should fall back to the
  auto-generated title (first 7 words of the text) for
  those annotations and continue with the rest.
- What happens when the output directory does not exist?
  The system should create it automatically (consistent
  with existing save_annotations behavior).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a prompt named
  `kindle-import-annotations` that accepts a Kindle HTML
  export file path as its only required parameter. The
  output directory is automatically derived as a `notes/`
  subdirectory inside the directory containing the export
  file.
- **FR-002**: The prompt MUST orchestrate three steps in
  sequence: parse annotations, generate titles, save
  files.
- **FR-003**: The title generation step MUST use a
  lightweight AI model to produce a concise title (under
  10 words) for each annotation based on its text
  content.
- **FR-004**: The prompt MUST return instructions that
  tell the MCP client to call `parse_kindle_export`,
  then generate titles for each annotation, then call
  `save_annotations` with the completed data.
- **FR-005**: If the title generation fails for any
  annotation, the system MUST fall back to the
  auto-generated title (first 7 words, title-cased) and
  continue processing.
- **FR-006**: The prompt response MUST include the file
  path, the derived output directory (`notes/` inside
  the export file's parent directory), and step-by-step
  instructions so the MCP client can execute the
  workflow.
- **FR-007**: The prompt MUST reuse the existing
  `parse_kindle_export` and `save_annotations` tools
  without modification.

### Key Entities

- **Kindle Export File**: An HTML file exported from the
  Kindle app containing highlighted annotations with
  metadata (book title, author, chapters, pages,
  locations, highlight colors).
- **Annotation**: A single highlighted passage with
  metadata. Initially has no title; title is generated
  during the workflow.
- **Output Directory**: A `notes/` subdirectory inside
  the parent directory of the Kindle export file.
  Automatically derived; created if it does not exist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can import a full Kindle export into
  individual annotation files with a single prompt
  invocation.
- **SC-002**: 100% of annotations from the export are
  saved as individual files with correct metadata.
- **SC-003**: Each annotation file has a meaningful,
  human-readable title generated from the annotation
  text.
- **SC-004**: The complete import workflow (parse +
  title generation + save) completes in under 60 seconds
  for a typical book with up to 200 annotations.

## Clarifications

### Session 2026-04-06

- Q: Where should annotation files be saved? → A: In a
  `notes/` subdirectory inside the directory containing
  the Kindle export file. The prompt derives this
  automatically from the file path — no separate output
  directory parameter needed.

## Assumptions

- The MCP client (e.g., Claude) is responsible for
  executing the tool calls described in the prompt
  response. The prompt provides instructions; the client
  orchestrates execution.
- The lightweight AI model for title generation is
  available to the MCP client as a subagent capability.
  The prompt instructs the client to use it but does not
  invoke it directly.
- The existing `parse_kindle_export` and
  `save_annotations` tools work correctly and are
  already registered in the MCP server.
- The prompt follows the same pattern as the existing
  `generate_book_index` prompt — it returns structured
  instructions as user messages that the MCP client
  executes.

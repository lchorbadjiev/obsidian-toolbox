# Feature Specification: Boox Import Annotations Prompt

**Feature Branch**: `012-boox-import-prompt`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "I want to have a prompt
book-import-annotations that support a workflow similar to
the kindle_import_annotations but for Boox annotations"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Invoke Boox Import via MCP Prompt (Priority: P1)

As an AI agent (e.g., Claude) connected to the MCP server, I
want to invoke a `boox_import_annotations` prompt that returns
step-by-step instructions for importing Boox annotations so
that I can orchestrate the full workflow — parse, generate
titles, and save — in a single guided interaction.

**Why this priority**: This is the entire feature — an MCP
prompt that guides the agent through the Boox import workflow,
mirroring the existing Kindle import prompt pattern.

**Independent Test**: Call the `boox_import_annotations` prompt
with a directory path and verify it returns a multi-step
instruction message referencing the correct tools
(`parse_boox_export`, `save_annotations`).

**Acceptance Scenarios**:

1. **Given** a user provides a Boox export directory path,
   **When** the `boox_import_annotations` prompt is invoked,
   **Then** it returns a message with step-by-step instructions
   for parsing, title generation, and saving annotations.
2. **Given** the prompt is invoked, **When** the instructions
   reference tool calls, **Then** they use `parse_boox_export`
   for parsing and `save_annotations` for writing output.
3. **Given** the export directory contains an EPUB file,
   **When** the instructions are followed, **Then** the
   workflow includes figure extraction alongside annotation
   parsing.

---

### User Story 2 - Title Generation Step (Priority: P1)

As an AI agent following the prompt instructions, I want the
workflow to include a title generation step using a lightweight
model so that each annotation gets a concise, meaningful title
before being saved.

**Why this priority**: Title generation is the key value-add
of the prompt-guided workflow over direct tool calls. Without
it, annotations would be saved with auto-generated titles
from `_title_from_text` which are less meaningful.

**Independent Test**: Verify the prompt instructions include a
title generation step that processes annotations in batches
using a subagent.

**Acceptance Scenarios**:

1. **Given** the prompt output, **When** the agent reads the
   instructions, **Then** Step 2 describes reading annotations
   in batches of ~30 and generating titles via a lightweight
   model.
2. **Given** title generation fails for some annotations,
   **When** the agent follows the instructions, **Then** those
   annotations are saved with their existing auto-generated
   titles.

---

### Edge Cases

- What happens when the directory path is invalid? The prompt
  still returns instructions; the error surfaces when the agent
  calls `parse_boox_export`.
- What happens when the directory has no annotations? The
  `parse_boox_export` tool handles this and returns an empty
  list.
- How does the prompt handle the output directory? It derives
  the output directory as a `notes/` subdirectory next to the
  input, matching the Kindle prompt pattern.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an MCP prompt named
  `boox_import_annotations` that accepts a directory path
  parameter.
- **FR-002**: The prompt MUST return a structured message with
  step-by-step instructions for the complete import workflow.
- **FR-003**: Step 1 MUST instruct the agent to call
  `parse_boox_export` with the provided directory path.
- **FR-004**: Step 2 MUST instruct the agent to generate
  concise titles for each annotation using a lightweight model
  (e.g., Haiku) in batches of approximately 30 annotations.
- **FR-005**: Step 3 MUST instruct the agent to call
  `save_annotations` with the annotations and a derived output
  directory (`notes/` subdirectory relative to the input path).
- **FR-006**: The prompt MUST derive the output directory
  automatically from the input path (parent directory + `notes/`).
- **FR-007**: The instructions MUST mention that figure images
  will be extracted automatically if an EPUB is present in the
  directory.
- **FR-008**: The instructions MUST include a final reporting
  step telling the agent to report the number of files written
  and output directory path.

### Key Entities

- **MCP Prompt**: A registered prompt in the MCP server that
  returns instructional messages to guide an AI agent through
  a multi-step workflow.
- **Workflow Steps**: Parse → Generate Titles → Save — the
  three-phase pattern shared with the Kindle import prompt.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The `boox_import_annotations` prompt is callable
  from any MCP client and returns a valid message.
- **SC-002**: Following the returned instructions from start to
  finish produces saved annotation markdown files with
  agent-generated titles.
- **SC-003**: The workflow completes successfully for Boox
  exports both with and without an accompanying EPUB file.
- **SC-004**: The prompt output references only existing MCP
  tools — no broken or nonexistent tool names.

## Assumptions

- The prompt follows the same structural pattern as the
  existing `kindle_import_annotations` prompt (three steps:
  parse, generate titles, save).
- The output directory is derived as `{input_dir}/notes/`,
  matching the Kindle import convention.
- The `parse_boox_export` MCP tool already exists and returns
  annotations as a list of dicts.
- The `save_annotations` MCP tool already exists and accepts
  annotations as inline dicts or via a file path.
- Title generation uses the same batched subagent approach as
  the Kindle prompt (batches of ~30, lightweight model).

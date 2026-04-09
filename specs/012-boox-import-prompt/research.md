# Research: Boox Import Annotations Prompt

**Feature**: 012-boox-import-prompt
**Date**: 2026-04-09

## R1: Prompt Pattern

**Decision**: Follow the exact same pattern as
`kindle_import_annotations` — a `@mcp.prompt` decorated
function that returns `list[UserMessage]` with structured
step-by-step instructions.

**Rationale**: The Kindle prompt is proven and well-tested.
The Boox workflow is analogous: parse → generate titles → save.
Reusing the pattern ensures consistency for AI agents that may
use both prompts.

**Differences from Kindle prompt**:

- Uses `parse_boox_export` instead of `parse_kindle_export`
- `parse_boox_export` returns annotations directly (not via
  temp file), so the title generation step works on the
  returned list rather than reading from a temp file
- Mentions that figure images are extracted automatically
  when an EPUB is present in the directory

**Alternatives considered**:

- Combined prompt for both Kindle and Boox: Would add
  complexity and conditional logic. Separate prompts are
  simpler and more discoverable.

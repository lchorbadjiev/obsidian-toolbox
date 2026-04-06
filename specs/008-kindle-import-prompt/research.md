# Research: Kindle Import Annotations Prompt

**Feature**: 008-kindle-import-prompt
**Date**: 2026-04-06

## R1: MCP Prompt Pattern

**Decision**: Follow the existing `generate_book_index`
prompt pattern — return a `list[UserMessage]` containing
structured instructions that the MCP client executes.

**Rationale**: The existing prompt pattern is proven and
consistent with the project's MCP architecture. The prompt
does not execute tools itself; it returns instructions
that tell the MCP client which tools to call and in what
order. This keeps the prompt stateless and testable.

**Alternatives considered**:

- Server-side orchestration (prompt calls tools
  internally): Would require the MCP server to act as an
  agent, which is outside the scope of the stdio
  transport and MCP prompt contract.
- Separate CLI command: Already exists implicitly via
  `parse_kindle_export` + `save_annotations`, but the
  prompt adds the title generation step that requires AI.

## R2: Prompt Instruction Structure

**Decision**: The prompt takes a single `file_path`
parameter and derives the output directory as `notes/`
inside the file's parent directory. It instructs the MCP
client to:
1. Call `parse_kindle_export(path)` to get annotations.
2. For each annotation, generate a concise title (under
   10 words) from the annotation text.
3. Set the `title` field on each annotation dict.
4. Call `save_annotations(annotations, directory)` where
   directory is `<parent of file_path>/notes/`.

**Rationale**: This mirrors the three-step workflow from
the spec. The prompt provides the exact tool names,
parameter shapes, and sequencing. The MCP client (e.g.,
Claude) interprets and executes these instructions.

**Alternatives considered**:

- Return multiple messages (one per step): Overcomplicates
  the prompt for no benefit. A single message with
  numbered steps is clearer.

## R3: Title Generation Instructions

**Decision**: Instruct the MCP client to generate titles
using its own AI capability (subagent or inline), with a
fallback to the first 7 words of the text (title-cased)
if generation fails.

**Rationale**: The MCP prompt cannot invoke AI models
directly — it returns text that the client interprets.
The prompt should specify the desired output format
(concise, under 10 words) and the fallback strategy.
The spec mentions "subagent running haiku" — the prompt
will instruct the client to use a lightweight model for
title generation.

**Alternatives considered**:

- Pre-generate titles server-side: Would require the MCP
  server to have its own AI client, adding a dependency
  and violating Constitution Principle V (Simplicity).

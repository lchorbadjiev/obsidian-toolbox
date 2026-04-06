# Research: Improve Kindle Import MCP Tools

**Date**: 2026-04-06
**Feature**: 009-kindle-import-file-passing

## R1: Temp File Strategy

**Decision**: Use `tempfile.NamedTemporaryFile` with
`delete=False` and `.json` suffix to create the intermediate
annotations file.

**Rationale**: The stdlib `tempfile` module handles
cross-platform temp directory resolution, unique naming, and
avoids race conditions. `delete=False` ensures the file
persists between the parse and save tool calls (which are
separate MCP invocations). The `.json` suffix makes the file
inspectable by humans and tools.

**Alternatives considered**:

- Writing next to the input file: rejected because the input
  directory may be read-only or cluttered.
- In-memory caching (module-level dict): rejected because MCP
  tools should be stateless between invocations; file-based
  passing is explicit and debuggable.
- Using `tempfile.mkstemp`: viable but `NamedTemporaryFile`
  with `delete=False` is more idiomatic and handles the file
  descriptor cleanly.

## R2: JSON Serialization Format

**Decision**: Use `json.dump` with the existing annotation
dict schema (`_annotation_to_dict` output). The temp file
contains a JSON array of annotation objects.

**Rationale**: The annotation dict format is already
well-defined and used by the inline `annotations` parameter.
Reusing it means `_dict_to_annotation` works unchanged for
deserialization. No schema migration needed.

**Alternatives considered**:

- Custom binary format: rejected (violates Principle V
  simplicity, no performance need).
- JSONL (one object per line): viable for streaming but
  unnecessary; the full array is written and read atomically.

## R3: Backward Compatibility for save_annotations

**Decision**: Make `annotations` and `file_path` mutually
exclusive optional parameters. Validate that exactly one is
provided at call time; raise `ValueError` if both or neither
are given.

**Rationale**: The spec requires backward compatibility
(FR-004) and mutual exclusion (FR-010). MCP tool parameters
can be optional with defaults of `None`, and validation
happens in the function body.

**Alternatives considered**:

- Two separate tools (`save_annotations` and
  `save_annotations_from_file`): rejected because it
  fragments the API surface and the spec explicitly calls
  for a single tool with two input modes.
- Overloaded type (union of list and str): rejected because
  MCP schema typing is clearer with named parameters.

## R4: Parse Tool Return Value Design

**Decision**: Return a dict with keys: `file_path` (str),
`count` (int), `book_title` (str), `author` (str),
`chapters` (list of str).

**Rationale**: FR-002 requires path, count, title, and
chapters. Adding `author` is useful context for the LLM
orchestrator at negligible cost. The dict stays well under
500 characters (SC-002).

**Alternatives considered**:

- Return only the file path: too minimal; the LLM needs
  count and metadata to plan batching without reading the
  file.
- Return a formatted string: harder for the LLM to parse
  programmatically; structured dict is better.

## R5: MCP Prompt Batch Size Guidance

**Decision**: The updated prompt will recommend batches of
~30 annotations for title generation, referencing the temp
file path and total count from the parse step.

**Rationale**: FR-007 specifies ~30. The original session
used 40-42 and experienced quality degradation in one batch.
30 balances quality (enough context per annotation) with
parallelism (e.g., 6 agents for 166 annotations).

**Alternatives considered**:

- Fixed batch size of 20: more conservative but creates
  too many parallel agents for large exports.
- Dynamic batch size based on text length: over-engineered
  for a prompt instruction; the LLM can adjust if needed.

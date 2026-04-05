# Research: Book Index Generation Prompt

## FastMCP Prompt Primitive

**Decision**: Use `@mcp.prompt()` decorator; return a single `UserMessage` containing the
formatted prompt text (book data + index generation instructions).

**Rationale**: FastMCP's prompt decorator accepts a function returning
`str | Message | Sequence[str | Message | dict]`. A single `UserMessage` with a rich text body
is the simplest correct form — one user turn with full context and instructions. The necessary
types (`Message`, `UserMessage`) are in `mcp.server.fastmcp.prompts.base`, which is already a
dependency via the existing `mcp` package.

**Alternatives considered**:
- Multi-turn messages (user + assistant): unnecessary complexity; a single user message with
  embedded instructions is sufficient for this prompt pattern.
- Return a plain `str`: works but loses the explicit `role: user` annotation that makes the
  MCP prompt contract explicit.

**Return type**: `list[Message]` annotated with `from mcp.server.fastmcp.prompts.base import Message`.
FastMCP validates and serializes this automatically.

---

## Error Handling for Prompts

**Decision**: Return a `UserMessage` with an error description when the directory does not
exist or is not a directory (rather than raising an exception).

**Rationale**: MCP prompts are expected to return messages in all cases. The calling agent
receives the error text as part of the conversation context and can handle it appropriately.
This is consistent with the per-file error tolerance pattern already used by
`parse_md_highlights_dir`.

**Alternatives considered**:
- Raise `FileNotFoundError` / `NotADirectoryError`: would surface as an MCP error response
  (not a prompt message). Less ergonomic for the calling agent.

---

## CLI Counterpart

**Decision**: Add `otb md index-prompt <directory>` command that prints the UserMessage text
to stdout.

**Rationale**: Constitution Principle I requires every feature to have a CLI entry point.
The underlying logic is shared with the MCP prompt function — the CLI calls the same helper
that builds the prompt text. This avoids logic duplication (Principle VI) and lets users
inspect or pipe the prompt without running an MCP client.

**Alternatives considered**:
- No CLI: violates Principle I.
- Separate implementation: violates Principle VI (no duplication between CLI and MCP).

---

## No New Dependencies

**Decision**: Zero new package dependencies. `UserMessage` / `Message` types are already
provided by the installed `mcp` package.

**Rationale**: Consistent with Principle V (Simplicity and Minimal Dependencies). All required
functionality is available in stdlib + existing packages.

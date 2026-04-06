<!--
SYNC IMPACT REPORT
==================
Version change: 1.3.0 → 1.4.1

Modified principles:
  VII. Document Formatting — Replaced markdownlint-cli (npx) with
       pymarkdownlnt (Python dev dependency). Added `pymarkdownlnt fix`
       for autofixing. Updated invocation to use `scan -r .` for
       recursive scanning and `fix -r .` for recursive autofixing.

Modified sections:
  Technology Stack — Updated markdown linting tool reference.
  Development Workflow — Updated pre-commit command.

Removed sections: N/A

Templates checked:
  ✅ .specify/templates/plan-template.md — No structural change needed.
  ✅ .specify/templates/spec-template.md — No structural change needed.
  ✅ .specify/templates/tasks-template.md — No structural change needed.
  ✅ .specify/templates/constitution-template.md — Source template;
     no changes needed.
  ✅ .specify/templates/commands/ — Directory is empty.

Follow-up TODOs: Update CLAUDE.md markdownlint command.
-->

# Obsidian Toolbox Constitution

## Core Principles

### I. CLI-First

Every feature MUST be exposed as a command under the `otb` Click CLI group defined in
`src/otb/cli.py`. Features without a CLI entry point are incomplete.

- Commands MUST follow the `otb <group> <subcommand>` pattern using `@click.group()` /
  `@click.command()`.
- Output goes to stdout; errors and warnings go to stderr.
- Commands MUST accept file paths as `click.Path` arguments — no hardcoded paths.

**Rationale**: The CLI is the primary user interface. Every capability must be reachable
without writing Python.

### II. Shared Parser Contract

All parsers MUST produce `list[Annotation]` using the `Annotation` dataclass
defined in `src/otb/parser.py`. Parser-specific data models are prohibited.

**Rationale**: A unified output contract allows CLI commands, MCP tools, and future
exporters to consume annotations from any source interchangeably.

### III. Test-First (NON-NEGOTIABLE)

Tests MUST be written and confirmed to fail before any implementation code is added.
The Red-Green-Refactor cycle is strictly enforced.

- Test fixtures MUST live in `tests/fixtures/` (HTML files and `tests/fixtures/annotations/`
  for markdown files).
- `uv run pytest` MUST pass with no failures before any commit.
- New parsers MUST have at least one fixture-based integration test.
- New MCP tools MUST have at least one test verifying tool inputs, outputs, and error
  responses conform to the MCP schema.

**Rationale**: Fixtures mirror real-world Kindle exports and markdown files. Test-first
prevents regressions and validates parser and MCP tool contracts against actual data.

### IV. Type Safety and Lint Quality

All code MUST satisfy `uv run mypy src/ tests/` (zero errors) and achieve a 10/10 score
from `uv run pylint src/ tests/`.

- Suppressing pylint rules is permitted only for established project-wide patterns
  already documented in `pyproject.toml` (e.g., `redefined-outer-name` for pytest
  fixtures).
- File-level suppressions (e.g., `missing-function-docstring`) are permitted in test
  files only.
- New suppressions MUST be justified by a comment explaining why the rule cannot be
  satisfied.

**Rationale**: Static analysis is a first-class quality gate. A 10/10 lint score and
clean mypy output are observable, machine-verifiable standards.

### V. Simplicity and Minimal Dependencies

Implementations MUST prefer the Python standard library over third-party packages.
Dependencies are added only when the stdlib cannot reasonably solve the problem.

- Markdown frontmatter MAY be parsed with `pyyaml` or with regex; `pyyaml` is an
  approved dependency for this specific use case.
- New dependencies (other than `pyyaml`) require explicit justification in the PR or
  commit message.
- YAGNI: no speculative abstractions, no premature configurability, no unused code paths.

**Rationale**: Fewer dependencies mean fewer attack surfaces, faster installs, and
simpler maintenance. `pyyaml` is explicitly permitted for frontmatter parsing where
regex becomes unwieldy; all other stdlib-replaceable packages remain prohibited.

### VI. MCP Server (stdio Transport)

The `otb` tool MUST expose its capabilities as an MCP (Model Context Protocol) server
using the stdio transport, enabling AI agents and MCP-compatible clients to invoke otb
tools programmatically.

- The MCP server MUST be launchable via `otb mcp` (or a dedicated script entry point)
  that starts the stdio-based server process.
- Every user-facing CLI capability MUST also be registered as an MCP tool with an
  equivalent name, description, and parameter schema.
- MCP tool handlers MUST delegate to the same underlying parser/service functions used
  by CLI commands — logic duplication between CLI and MCP layers is prohibited.
- The stdio transport is the only supported transport. HTTP/SSE transport MUST NOT be
  added without a MINOR constitution amendment.
- MCP tool inputs and outputs MUST be typed and validated; untyped `dict` interfaces
  are prohibited.

**Rationale**: MCP enables AI agents (including Claude) to call otb tools directly
without shell invocation. stdio is the simplest, most portable transport and aligns
with Principle V (Simplicity). Sharing implementation with CLI (Principle I) prevents
drift between the two interfaces.

### VII. Document Formatting

All markdown documents produced during the speckit workflow — including
specs, plans, tasks, research notes, quickstart guides, data models, and
contract definitions — MUST wrap prose lines at 80 characters.

- Hard line breaks MUST be used for prose paragraphs and bullet points;
  do not rely on soft-wrap rendering.
- Code blocks, tables, and wikilinks are exempt from the 80-character
  limit when wrapping would break syntax or readability.
- Frontmatter (YAML) values are exempt.
- Headings are exempt (keep them on one line).

All markdown files committed to the repository MUST pass
`pymarkdownlnt scan <file>` with zero errors before committing.
Use `pymarkdownlnt fix <file>` to autofix easy formatting issues.
This applies to every `.md` file: README, specs, plans, tasks,
research notes, quickstart guides, data models, and contract
definitions.

- Run `pymarkdownlnt scan -r --respect-gitignore .` from the repo root to check all
  files recursively (respects `.pymarkdown.json` config).
- To scan a single file: `pymarkdownlnt scan path/to/file.md`
- To autofix: `pymarkdownlnt fix -r --respect-gitignore .` or
  `pymarkdownlnt fix path/to/file.md`
- If a rule conflicts with a legitimate formatting need (e.g. a
  long URL that cannot be wrapped), disable the specific rule
  inline with a `<!-- pyml disable-next-line md0XX-->` comment
  and add a one-line justification comment immediately above it.
- Project-wide rule overrides MUST be recorded in
  `.pymarkdown.json` at the repo root.

**Rationale**: Consistent line width makes diffs readable, enables
side-by-side comparison in terminals and code review tools, and ensures
documents render predictably in any Markdown viewer or editor.
Automated linting catches formatting regressions that manual review
misses.

## Technology Stack

- **Language**: Python 3.12+
- **Package manager**: uv (`uv sync` to install, `uv run <cmd>` to execute)
- **CLI framework**: Click (registered as `otb` script in `pyproject.toml`)
- **MCP framework**: MCP Python SDK (`mcp`) — stdio transport only
- **Testing**: pytest with fixture files in `tests/fixtures/`
- **Type-checking**: mypy (strict, zero-error target)
- **Linting**: pylint (10/10 target)
- **Markdown linting**: pymarkdownlnt (`pymarkdownlnt scan` to check, `pymarkdownlnt fix` to autofix; zero-error target)
- **Project layout**: `src` layout — package root at `src/otb/`

Adding or removing a technology from this stack constitutes a MINOR amendment if additive
or a MAJOR amendment if a listed tool is removed or replaced.

## Development Workflow

- **Before committing**: `uv run pytest` AND `uv run mypy src/ tests/` AND
  `uv run pylint src/ tests/` AND `pymarkdownlnt scan -r --respect-gitignore .` MUST all
  pass cleanly.
- **New parser**: add fixture → write failing test → implement → verify green.
- **New CLI command**: add Click command → wire to parser or service function → add
  integration test covering the command output.
- **New MCP tool**: register tool in MCP server → write failing test verifying schema
  and response → delegate to existing service function → verify green.
- **Issue tracking**: use `bd` (beads). Run `bd prime` for workflow context.
  - `bd ready` — find unblocked work
  - `bd create "Title" --type task --priority 2` — create issue
  - `bd close <id>` — complete work

All PRs and agent-assisted implementations MUST verify compliance with Core Principles
before merging.

## Governance

This constitution supersedes all other development guidelines. In case of conflict,
the constitution takes precedence.

**Amendment procedure**:
1. Identify which version bump applies (MAJOR / MINOR / PATCH per semantic versioning).
2. Update this file: revise the relevant section, increment `CONSTITUTION_VERSION`,
   set `LAST_AMENDED_DATE` to today's date.
3. Run the consistency propagation checklist against all `.specify/templates/` files.
4. Commit with message: `docs: amend constitution to vX.Y.Z (<summary of change>)`.

**Versioning policy**:
- MAJOR: principle removal, redefinition, or backward-incompatible governance change.
- MINOR: new principle or section added, or materially expanded guidance.
- PATCH: clarifications, wording, typo fixes, non-semantic refinements.

**Compliance review**: Every implementation plan MUST include a Constitution Check
section (see `.specify/templates/plan-template.md`). Violations MUST be justified in
the Complexity Tracking table.

Use `CLAUDE.md` for runtime development guidance (commands, architecture, file layout).

**Version**: 1.4.1 | **Ratified**: 2026-04-03 | **Last Amended**: 2026-04-06

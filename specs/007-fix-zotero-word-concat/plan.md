# Implementation Plan: Fix Zotero Word Concatenation

**Branch**: `007-fix-zotero-word-concat` | **Date**: 2026-04-06
| **Spec**: [spec.md](spec.md)
**Input**: Feature specification from
`/specs/007-fix-zotero-word-concat/spec.md`

Prose lines MUST wrap at 80 characters (Constitution
Principle VII).

## Summary

Add aspell-based word-splitting to the Zotero annotation
parser. Concatenated words like "isthat" and
"SoftwareWithout" are detected using aspell's pipe mode and
automatically split into "is that" and "Software Without".
The splitting is integrated into
`parse_zotero_annotations()` so all consumers (CLI, MCP)
get clean text. A `--verbose` flag exposes individual fixes.

## Technical Context

**Language/Version**: Python 3.12+ + click, mcp (FastMCP)
— already installed; no new deps
**Primary Dependencies**: aspell (system command-line tool,
not a Python package)
**Storage**: Filesystem (reads Zotero exports, writes
markdown via existing `md_writer.py`)
**Testing**: pytest with fixtures in `tests/fixtures/zotero/`
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI tool + MCP server
**Performance Goals**: Word-splitting adds < 2s for 300
annotations (~200ms measured for aspell pipe mode)
**Constraints**: No new Python dependencies (Constitution
Principle V); aspell is a system dependency
**Scale/Scope**: Single book export at a time; hundreds of
annotations per file at most

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after
Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | PASS | Existing `otb zotero parse` updated with `--verbose` |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` unchanged |
| III. Test-First | PASS | Tests for word-splitting written first |
| IV. Type Safety & Lint | PASS | mypy + pylint targets maintained |
| V. Simplicity | PASS | subprocess call to aspell; no new Python deps |
| VI. MCP Server | PASS | `parse_zotero_export` gets clean text automatically |
| VII. Document Formatting | PASS | 80-char wrapping enforced |

No violations. Complexity Tracking table not needed.

## Project Structure

### Documentation (this feature)

```text
specs/007-fix-zotero-word-concat/
├── spec.md
├── plan.md              # This file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   └── mcp.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
src/otb/
├── word_fixer.py      # NEW: aspell-based word splitting
├── zotero_parser.py   # MODIFIED: integrate word_fixer
├── cli.py             # MODIFIED: add --verbose flag
├── mcp_server.py      # UNCHANGED (gets clean text via parser)
├── parser.py          # UNCHANGED
├── md_parser.py       # UNCHANGED
└── md_writer.py       # UNCHANGED

tests/
├── test_word_fixer.py     # NEW: unit tests for word splitting
├── test_zotero_parser.py  # MODIFIED: add word-split assertions
├── test_cli_zotero.py     # MODIFIED: add --verbose test
└── fixtures/zotero/       # EXISTING
    ├── Annotations.md
    └── book.txt
```

**Structure Decision**: New `word_fixer.py` module isolates
aspell integration from the parser. This keeps
`zotero_parser.py` focused on format parsing and makes the
word-splitting logic independently testable and reusable.

## Implementation Phases

### Phase 1: Word Fixer Module (test-first)

1. Create `tests/test_word_fixer.py` with failing tests:
   - Test `fix_words()` splits "isthat" → "is that".
   - Test "SoftwareWithout" → "Software Without".
   - Test legitimate words ("cannot", "without") unchanged.
   - Test allowlisted words ("superclass", "codebase")
     unchanged.
   - Test short words (< 4 chars) not split.
   - Test aspell not found raises `RuntimeError`.
   - Test empty input returns empty output.
   - Test fix count tracking.

2. Create `src/otb/word_fixer.py`:
   - `check_aspell_available() -> None` — raises
     `RuntimeError` if aspell not found.
   - `fix_concatenated_words(texts: list[str], verbose:
     bool = False) -> tuple[list[str], int]` — returns
     cleaned texts and fix count.
   - Internal `_ALLOWLIST` set of known compound words.
   - Internal `_get_replacements(words: set[str]) ->
     dict[str, str]` — runs aspell pipe mode, parses
     suggestions, filters by allowlist and min length.

3. Verify: `uv run pytest tests/test_word_fixer.py` green.

### Phase 2: Parser Integration

1. Update `tests/test_zotero_parser.py`:
   - Test that known concatenated words in fixture are
     split in parsed output.
   - Test annotation count unchanged (splitting does not
     add/remove annotations).

2. Update `src/otb/zotero_parser.py`:
   - Import `fix_concatenated_words` and
     `check_aspell_available`.
   - Call `check_aspell_available()` at start.
   - After regex extraction, call
     `fix_concatenated_words()` on all annotation texts.
   - Print fix count summary to stderr.

3. Verify: `uv run pytest tests/test_zotero_parser.py`
   green.

### Phase 3: CLI Verbose Flag

1. Update `tests/test_cli_zotero.py`:
   - Test `--verbose` flag prints individual word fixes.
   - Test default mode still prints summary count.

2. Update `src/otb/cli.py`:
   - Add `--verbose` option to `zotero parse` command.
   - Pass verbose flag through to
     `parse_zotero_annotations()`.

3. Verify: `uv run pytest tests/test_cli_zotero.py` green.

### Phase 4: Quality Gates

1. `uv run pytest` — all tests pass.
2. `uv run mypy src/ tests/` — zero errors.
3. `uv run pylint src/ tests/` — 10/10.
4. `pymarkdownlnt scan "**/*.md"` — zero errors.

## Post-Phase 1 Constitution Re-Check

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. CLI-First | PASS | `--verbose` flag added |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Tests written before implementation |
| IV. Type Safety & Lint | PASS | mypy + pylint clean |
| V. Simplicity | PASS | subprocess + allowlist, no new deps |
| VI. MCP Server | PASS | Gets clean text via parser |
| VII. Document Formatting | PASS | 80-char prose, markdownlint clean |

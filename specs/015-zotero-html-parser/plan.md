# Implementation Plan: Parse Zotero HTML Exports with Colors

**Branch**: `015-zotero-html-parser` | **Date**: 2026-04-09 |
**Spec**: [spec.md](spec.md)

**Note**: Prose lines MUST wrap at 80 characters
(Constitution Principle VII).

## Summary

Add an HTML parser for Zotero annotation exports that preserves
highlight colors. The parser reads `Annotations.html` using
BeautifulSoup (already a dependency), extracts annotation text,
page numbers, and color from the HTML structure. The existing
`parse_zotero_annotations` function auto-detects which format is
present (HTML preferred over markdown). All downstream features
(word fixing, figure extraction, merge) work identically.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: `beautifulsoup4` (already installed)
**Storage**: Filesystem
**Testing**: pytest with HTML fixture
**Target Platform**: macOS / Linux CLI
**Project Type**: CLI + MCP library
**Performance Goals**: N/A
**Constraints**: No new dependencies
**Scale/Scope**: New parsing function in `zotero_parser.py`
(~50 lines) + format detection logic

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. CLI-First | PASS | `otb zotero parse` unchanged |
| II. Shared Parser Contract | PASS | Returns `list[Annotation]` |
| III. Test-First | PASS | Tests planned |
| IV. Type Safety | PASS | mypy + pylint 10/10 |
| V. Simplicity | PASS | Uses existing bs4 dep |
| VI. MCP Server | PASS | Transparent |
| VII. Doc Formatting | PASS | Wrapped at 80 chars |

No violations.

## Project Structure

### Source Code

```text
src/otb/
├── zotero_parser.py     # MODIFY: add HTML parser + detection
└── md_writer.py         # MODIFY: include color in frontmatter

tests/
├── fixtures/
│   └── zotero/
│       └── Annotations.html  # NEW: HTML fixture
├── test_zotero_parser.py     # MODIFY: add HTML tests
└── test_md_writer.py         # MODIFY: verify color output
```

**Structure Decision**: Add HTML parsing directly in
`zotero_parser.py` alongside the existing markdown parser.
The public `parse_zotero_annotations` function detects format
and delegates to the appropriate internal parser. No new
module needed.

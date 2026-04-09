# Research: Boox Annotation Parser

**Feature**: 010-boox-parser
**Date**: 2026-04-09

## R1: Boox Export File Format

**Decision**: The Boox annotation export is a plain-text file with
a well-defined line-based structure. Parse it with a simple state
machine using regex and string operations.

**Rationale**: The format is straightforward — no nested
structures, no escaping, no encoding issues beyond UTF-8. A
line-based parser with regex for the date/page pattern is the
simplest correct approach.

**Alternatives considered**:

- Formal grammar / PEG parser: Overkill for a flat,
  line-delimited format.
- CSV/TSV parsing: The format is not tabular.

### Format Analysis

Based on the sample file
`tmp/just-for-fun-torvalds/Just for Fun_...annotation-...txt`:

```text
Reading Notes | <<BOOK_TITLE>>AUTHOR_NAME     ← header (line 1)
CHAPTER_TITLE                                  ← chapter heading
YYYY-MM-DD HH:MM  |  Page No.: NNN            ← date/page
ANNOTATION TEXT LINE 1                         ← text (may span
ANNOTATION TEXT LINE 2                            multiple lines)
-------------------                            ← separator
CHAPTER_TITLE                                  ← new chapter
YYYY-MM-DD HH:MM  |  Page No.: NNN            ← next annotation
...
```

**Key patterns**:

- Header line: starts with `Reading Notes |`
- Separator: line of 3+ dashes (`---+`)
- Date/page: matches
  `\d{4}-\d{2}-\d{2} \d{2}:\d{2}\s+\|\s+Page No\.: (.+)`
- Chapter heading: any non-empty line that appears after a
  separator (or header) and before a date/page line
- Annotation text: all lines between date/page and next separator

## R2: Reuse of parse_book_metadata

**Decision**: Reuse `parse_book_metadata` from `zotero_parser.py`
as-is. The `book.txt` format is identical between Zotero and Boox
exports (alternating label/value lines).

**Rationale**: The sample `book.txt` in
`tmp/just-for-fun-torvalds/` uses exactly the same format as the
Zotero fixture in `tests/fixtures/zotero/book.txt`. No adaptation
needed.

**Alternatives considered**:

- Duplicate the function: Violates DRY and Constitution
  Principle V.
- Move to a shared module: Premature — only two consumers.
  Import from `zotero_parser` is sufficient.

## R3: Annotation File Discovery

**Decision**: The parser will look for exactly one `.txt` file in
the directory that is not `book.txt`. If zero or multiple
candidates are found, raise an error.

**Rationale**: Boox exports place one annotation file per
directory. The filename includes the book title and a timestamp,
so it varies. Glob for `*.txt` excluding `book.txt` is the
simplest correct approach.

**Alternatives considered**:

- Require a specific filename pattern: Too brittle — the Boox
  naming convention includes truncated titles.
- Accept the annotation file as an explicit argument: Adds
  friction for the user when the directory convention is
  unambiguous.

## R4: Word Concatenation Fixing (aspell)

**Decision**: Do NOT use `fix_concatenated_words` / aspell for
Boox annotations. Unlike Zotero OCR-based exports, Boox
annotations are direct text highlights from reflowed ePub/PDF
content and do not exhibit concatenated-word artifacts.

**Rationale**: The sample file shows clean text with no
concatenated words. Adding aspell as a dependency for Boox would
violate Principle V and add latency for no benefit.

**Alternatives considered**:

- Optional aspell pass: Unnecessary complexity for a problem
  that doesn't exist in this format.

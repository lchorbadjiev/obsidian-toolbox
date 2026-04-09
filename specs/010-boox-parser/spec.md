# Feature Specification: Boox Annotation Parser

**Feature Branch**: `010-boox-parser`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "I have an exported annotations from
Boox device stored in @tmp/just-for-fun-torvalds/ directory. I need
a new parser similar to zotero_parser.py named boox_parser that
reads these annotations and transforms them into list of
Annotations."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse Boox Annotations (Priority: P1)

As a user who highlights passages on a Boox e-reader, I want to
import my exported annotations into the system so that they become
standard Annotation objects I can use with existing tools (markdown
export, Anki cards, MCP prompts).

**Why this priority**: This is the core and only feature — without
parsing, nothing else works.

**Independent Test**: Can be fully tested by pointing the parser at
a directory containing a Boox annotation export and verifying that
it returns a correct list of Annotation objects with book metadata,
chapter names, page numbers, and highlight text.

**Acceptance Scenarios**:

1. **Given** a directory with `book.txt` and a Boox annotation
   `.txt` file, **When** the parser is invoked on that directory,
   **Then** it returns a list of Annotation objects — one per
   highlighted passage.
2. **Given** a valid Boox export, **When** the parser processes
   annotations that include chapter headings, **Then** each
   Annotation has its `chapter` field set to the most recent
   chapter heading encountered before it.
3. **Given** a valid Boox export, **When** the parser processes
   each annotation, **Then** the `location` field contains the
   page number (as integer) from the "Page No.:" line, the
   `page` field is empty string, the `book` field contains
   title and author from `book.txt`, and the `text` field
   contains the full highlighted passage.

---

### User Story 2 - Handle Multi-line Annotations (Priority: P1)

As a user, I want annotations that span multiple lines in the
export file to be captured as a single complete annotation so that
no highlighted text is lost or truncated.

**Why this priority**: Boox exports contain multi-line highlights
separated by dashed-line delimiters. Correct boundary detection is
essential for accurate parsing.

**Independent Test**: Parse an export containing a multi-line
annotation and verify the full text (across all lines) appears in
a single Annotation object.

**Acceptance Scenarios**:

1. **Given** an annotation whose text spans multiple lines before
   the next `---` separator, **When** the parser processes it,
   **Then** all lines are joined into the Annotation's `text`
   field.
2. **Given** consecutive annotations separated by `---` lines,
   **When** the parser processes them, **Then** each annotation
   is a distinct Annotation object with only its own text.

---

### User Story 3 - Consistent Numbering (Priority: P2)

As a user, I want each parsed annotation to have a sequential
number so that annotations are consistently ordered for downstream
tools.

**Why this priority**: Sequential numbering is used by existing
export and display tools. It is low-effort but required for
integration.

**Independent Test**: Parse a file with multiple annotations and
verify `number` fields run from 1 to N without gaps.

**Acceptance Scenarios**:

1. **Given** a Boox export with N annotations, **When** the
   parser processes them, **Then** each Annotation's `number`
   field is assigned sequentially starting at 1.

---

### Edge Cases

- What happens when the annotation file is missing from the
  directory? The parser should raise a clear error.
- What happens when `book.txt` is missing? The parser should
  raise a clear error.
- What happens when an annotation block has a date/page line
  but no text before the next separator? The parser should
  skip it rather than creating an empty annotation.
- How does the system handle chapter headings that are just
  Roman numerals (e.g., "I", "III") vs. full titles (e.g.,
  "V: The Beauty of Programming")? Both formats should be
  accepted as chapter headings.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse Boox annotation export
  directories that contain a `book.txt` metadata file and a
  `.txt` annotation file.
- **FR-002**: System MUST extract book title and author from
  `book.txt` (label/value pair format, same as Zotero exports)
  and populate the `Book` dataclass.
- **FR-003**: System MUST recognize the first line of the
  annotation file as a header line containing the book title
  and author, and skip it during annotation extraction.
- **FR-004**: System MUST detect chapter headings that appear
  as standalone lines between annotation blocks and track the
  current chapter for subsequent annotations.
- **FR-005**: System MUST extract the page number from lines
  matching the pattern `YYYY-MM-DD HH:MM  |  Page No.: NNN`
  and store it as an integer in the Annotation's `location`
  field. The `page` field is set to empty string (Boox
  exports have no separate page concept).
- **FR-006**: System MUST capture all text lines between a
  date/page line and the next `---` separator as the
  annotation text, joining multiple lines into a single string.
- **FR-007**: System MUST auto-generate a title for each
  annotation from the first sentence of its text (up to 7
  words, title-cased), consistent with the existing
  `_title_from_text` behavior.
- **FR-008**: System MUST assign sequential numbers starting
  at 1 to all parsed annotations.
- **FR-009**: System MUST raise a clear error when required
  files (`book.txt` or the annotation `.txt` file) are missing.
- **FR-010**: System MUST skip annotation blocks that have a
  date/page line but contain no text.
- **FR-011**: System MUST set `color` to `None` for all Boox
  annotations (color is not present in Boox exports).

### Key Entities

- **Book**: Represents book metadata (title, author) extracted
  from `book.txt`.
- **Annotation**: Represents a single highlighted passage with
  book reference, chapter, page, text, auto-generated title,
  and sequential number.
- **Boox Export Directory**: A directory containing `book.txt`
  and exactly one `.txt` annotation file whose name follows the
  Boox export naming convention.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All highlighted passages in a Boox export are
  parsed into individual Annotation objects with no data loss.
- **SC-002**: Chapter attribution is correct — each annotation
  is assigned to the chapter heading that most recently preceded
  it in the file.
- **SC-003**: Page numbers match the source file exactly for
  every annotation.
- **SC-004**: The parser output is fully compatible with
  existing downstream tools (markdown export, Anki card
  generation) without any adapter or transformation.
- **SC-005**: The parser handles the sample export in
  `tmp/just-for-fun-torvalds/` correctly, producing 35
  annotations with accurate metadata.

## Assumptions

- The Boox export format places `book.txt` and one annotation
  `.txt` file in the same directory (mirroring the Zotero
  export convention already supported).
- The `book.txt` file uses the same label/value pair format as
  Zotero exports (alternating label and value lines), so the
  existing `parse_book_metadata` function can be reused.
- The annotation `.txt` file's first line is always a header
  line starting with "Reading Notes |" that should be skipped.
- Annotation blocks are always separated by lines of dashes
  (`---`).
- Date/page lines always match the format
  `YYYY-MM-DD HH:MM  |  Page No.: NNN`.
- Lines that appear between separator blocks and are not
  date/page lines, and not annotation text continuation, are
  chapter headings.
- The parser does not need aspell-based word fixing (unlike
  Zotero exports, Boox exports do not suffer from concatenated
  word artifacts).

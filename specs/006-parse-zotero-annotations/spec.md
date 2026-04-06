# Feature Specification: Parse Zotero Annotations

**Feature Branch**: `006-parse-zotero-annotations`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "I have an export of book annotations
from Zotero. I need support for parsing Zotero annotations and
storing each annotation into a separate annotation markdown file."

## User Scenarios & Testing *(mandatory)*

### User Story 1 + Parse and write Zotero annotations (Priority: P1)

A user exports their book annotations from Zotero as a markdown
file. They run an `otb` CLI command pointing at the Zotero export
directory (which contains an `Annotations.md` file and a `book.txt`
metadata file) and an output directory. The tool parses each
annotation and writes one markdown file per annotation in the
existing annotation format (YAML frontmatter + heading +
blockquote + citation), matching the structure already used
by the Kindle-based workflow.

**Why this priority**: This is the entire feature. Without parsing
and writing, nothing else matters.

**Independent Test**: Can be fully tested by running the command on
the fixture directory and verifying the output files match the
expected annotation markdown format.

**Acceptance Scenarios**:

1. **Given** a Zotero export directory with `Annotations.md` and
   `book.txt`, **When** the user runs the parse command with an
   output directory, **Then** one markdown file is created per
   annotation with correct frontmatter, title, blockquote, and
   citation.
2. **Given** the same input, **When** the command completes,
   **Then** each output file has sequential numbering in the
   `number` frontmatter field and in the filename prefix
   (e.g., `001 + Title Here.md`).
3. **Given** an annotation with a very long text, **When** the
   file is generated, **Then** the title is auto-generated from
   the first sentence (up to 7 words, title-cased), consistent
   with the existing `Annotation.title` behavior.

---

### User Story 2 + Handle annotation edge cases (Priority: P2)

Some Zotero annotations are split across pages or contain only a
fragment (e.g., a single word like `"your design"` or `"If"`). The
parser handles these gracefully without crashing or producing
malformed output.

**Why this priority**: Real-world Zotero exports contain these
fragments. The tool must be robust, but this is secondary to the
core parsing path.

**Independent Test**: Can be tested by including fragment
annotations in fixtures and verifying they produce valid output
files.

**Acceptance Scenarios**:

1. **Given** an annotation that is a single word or very short
   fragment, **When** parsed, **Then** a valid markdown file is
   still produced with the fragment as both title and blockquote.
2. **Given** an annotation whose text contains line breaks or
   hyphenated word splits from PDF extraction, **When** parsed,
   **Then** the text is preserved as-is in the blockquote.

---

### Edge Cases

+ What happens when `book.txt` is missing from the directory?
  The command reports a clear error and exits.
+ What happens when `Annotations.md` is empty or contains only
  the header? The command produces no output files and exits
  cleanly.
+ What happens when the output directory already contains files?
  Existing files are not overwritten; the command reports a
  conflict.
+ What happens when an annotation line cannot be parsed (no
  page reference)? The annotation is skipped with a warning.

## Requirements *(mandatory)*

### Functional Requirements

+ **FR-001**: System MUST parse Zotero `Annotations.md` files
  where each annotation is a quoted string followed by a page
  reference in the format `("Title", p. XX)`.
+ **FR-002**: System MUST parse the companion `book.txt` file
  to extract book title and author.
+ **FR-003**: System MUST produce one markdown file per
  annotation, using the same format as existing annotation
  files (YAML frontmatter with `source`, `author`, `page`,
  `location`, `type: annotation`, `number`; heading; blockquote;
  citation). The `location` field is set to the page number.
+ **FR-004**: System MUST auto-generate a title from each
  annotation's text using the existing title generation logic
  (first sentence, up to 7 words, title-cased).
+ **FR-005**: System MUST number annotations sequentially
  starting from 1, reflected in both the filename prefix and
  the `number` frontmatter field.
+ **FR-006**: System MUST expose this functionality as a new
  `otb` CLI subcommand.
+ **FR-007**: System MUST reuse the existing `Book` and
  `Annotation` dataclasses from `parser.py`.

### Key Entities

+ **Zotero Annotations File**: A markdown file exported from
  Zotero containing highlighted passages, each as a quoted
  string with a book title and page reference.
+ **Book Metadata File**: A plain-text file (`book.txt`)
  containing key-value metadata about the book (title, author,
  publisher, etc.).
+ **Annotation Markdown File**: The output format -+ one file
  per annotation with YAML frontmatter, a heading, a blockquote,
  and a citation line.

## Success Criteria *(mandatory)*

### Measurable Outcomes

+ **SC-001**: All annotations from the Zotero fixture file are
  parsed and written as individual markdown files with zero data
  loss (every quoted passage in the input produces an output
  file).
+ **SC-002**: Output files are structurally identical to
  existing Kindle-sourced annotation files (same frontmatter
  fields, same heading/blockquote/citation layout).
+ **SC-003**: The command completes without errors on the
  provided fixture data.
+ **SC-004**: Round-trip consistency: output files can be read
  back by the existing markdown parser without errors.

## Clarifications

### Session 2026-04-06

+ Q: How should the `location` frontmatter field be populated
  for Zotero exports? → A: Use the page number as the location
  value.
+ Q: How should the citation line be formatted for Zotero
  annotations? → A: Mirror Kindle format exactly, omitting
  unavailable fields.

## Assumptions

+ The Zotero annotation format is consistent: each annotation
  is a quoted string followed by `("BookTitle", p. XX)` on a
  single line (possibly spanning multiple lines for long
  passages).
+ The `book.txt` file uses a two-line-per-field format where
  the field name is on one line and its value on the next.
+ The `chapter` frontmatter field is omitted (or left empty)
  because Zotero annotations do not include chapter information
  in the export.
+ The `location` frontmatter field is populated with the page
  number from the Zotero export (same value as the `page`
  field), ensuring compatibility with the existing `Annotation`
  dataclass.
+ No new dependencies are required; the implementation uses
  only existing project dependencies.

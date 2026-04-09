# Feature Specification: Parse Zotero HTML Exports with Colors

**Feature Branch**: `015-zotero-html-parser`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "Switch the Zotero parser from
parsing markdown export to parse HTML and keep the colors."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse Zotero HTML with Colors (Priority: P1)

As a user who exports Zotero annotations as HTML, I want the
parser to read the HTML export file and extract annotations
with their highlight colors preserved, so that my color-coded
reading notes retain their visual organization.

**Why this priority**: The HTML export is the primary format
that preserves highlight color information. The current
markdown parser loses colors because `Annotations.md` does
not include them.

**Independent Test**: Parse the HTML export from the sample
directory and verify each annotation has the correct color
value extracted from the `background-color` style attribute.

**Acceptance Scenarios**:

1. **Given** a Zotero export directory containing `book.txt`
   and an `Annotations.html` file, **When** the parser is
   invoked, **Then** it returns a list of Annotation objects
   with text, page, and color fields populated.
2. **Given** an HTML annotation with
   `background-color: #ffd40080`, **When** the parser extracts
   it, **Then** the Annotation's `color` field contains
   `"#ffd400"` (without the alpha channel suffix).
3. **Given** an HTML export with 4 different highlight colors,
   **When** all annotations are parsed, **Then** each
   annotation's color matches the original highlight color
   from the HTML.

---

### User Story 2 - Maintain All Existing Features (Priority: P1)

As a user, I want the HTML parser to support all existing
features — word concatenation fixing, PDF figure extraction,
cross-page annotation merging — so that switching from markdown
to HTML is seamless.

**Why this priority**: The HTML parser replaces the markdown
parser. All downstream features must continue to work.

**Independent Test**: Run the full pipeline (parse → fix words
→ merge → figure extraction → write) on the sample HTML export
and verify all features function correctly.

**Acceptance Scenarios**:

1. **Given** a Zotero HTML export with a PDF, **When** the
   parser runs the full pipeline, **Then** figures are
   extracted, split annotations are merged, and word
   concatenation issues are fixed.
2. **Given** the HTML parser, **When** annotations are saved
   as markdown, **Then** the output includes color in the
   frontmatter metadata.

---

### User Story 3 - Backward Compatibility (Priority: P2)

As a user who may still have markdown exports, I want the
parser to detect which format is present and parse accordingly
so that existing exports continue to work.

**Why this priority**: Users may have older exports in markdown
format. The parser should not break for them.

**Independent Test**: Run the parser on a directory with
`Annotations.md` (no HTML). Verify it falls back to the
existing markdown parser behavior.

**Acceptance Scenarios**:

1. **Given** a directory with `Annotations.html`, **When** the
   parser is invoked, **Then** it uses the HTML parser.
2. **Given** a directory with only `Annotations.md` (no HTML),
   **When** the parser is invoked, **Then** it falls back to
   the existing markdown parser.
3. **Given** a directory with both files, **When** the parser
   is invoked, **Then** it prefers the HTML export (richer
   data).

---

### Edge Cases

- What happens when the HTML file is malformed? The parser
  should attempt best-effort extraction and warn on
  unparseable elements.
- How are color values normalized? The HTML uses 8-digit hex
  with alpha (e.g., `#ffd40080`). The parser strips the alpha
  channel to produce a 6-digit hex color (e.g., `#ffd400`).
- What happens when an annotation has no color/highlight? The
  color field is set to `None`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse Zotero HTML annotation exports
  (`Annotations.html`) containing `<p>` elements with
  `<span class="highlight">` and `<span class="citation">`
  structure.
- **FR-002**: System MUST extract the annotation text from the
  highlighted `<span>` element.
- **FR-003**: System MUST extract the page number from the
  citation `<span>` element (pattern: `p. NNN`).
- **FR-004**: System MUST extract the highlight color from the
  `background-color` CSS style attribute and store it in the
  Annotation's `color` field as a 6-digit hex string (e.g.,
  `#ffd400`), stripping the alpha channel.
- **FR-005**: System MUST prefer `Annotations.html` over
  `Annotations.md` when both are present in the directory.
- **FR-006**: System MUST fall back to the existing markdown
  parser when only `Annotations.md` is present.
- **FR-007**: System MUST integrate with the existing word
  concatenation fixer, PDF figure extraction, and cross-page
  annotation merging features.
- **FR-008**: The `color` field MUST be included in the
  annotation markdown frontmatter when saving.

### Key Entities

- **Annotation**: The existing `Annotation` dataclass. The
  `color` field (already defined as `str | None`) is now
  populated from the HTML highlight color.
- **Zotero HTML Export**: An HTML file containing structured
  annotation elements with embedded color information.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All annotations from the sample HTML export are
  parsed with correct text, page number, and color values.
- **SC-002**: The 4 distinct highlight colors in the sample
  (`#ffd400`, `#2ea8e5`, `#f19837`, `#ff6666`) are preserved
  in the parsed annotations.
- **SC-003**: The annotation count from the HTML export matches
  the count from the markdown export (same source data).
- **SC-004**: All downstream features (word fixing, figure
  extraction, merge, markdown output) work identically with
  HTML input.
- **SC-005**: Existing markdown-based Zotero exports continue
  to parse correctly (backward compatibility).

## Assumptions

- The Zotero HTML export uses a consistent structure:
  `<p>` elements containing `<span class="highlight">` with
  an inner `<span style="background-color: #XXXXXXXX">` for
  the colored annotation text, and `<span class="citation">`
  for the book title and page reference.
- Color values in the HTML are 8-digit hex with alpha channel
  (e.g., `#ffd40080`). The last 2 digits (alpha) are stripped.
- The HTML export and markdown export contain the same
  annotations (same source data, different format).
- BeautifulSoup (already a project dependency) is used for
  HTML parsing, consistent with the Kindle parser.
- The `color` field on the `Annotation` dataclass already
  exists (`str | None`) and is currently `None` for Zotero
  annotations — this feature populates it.

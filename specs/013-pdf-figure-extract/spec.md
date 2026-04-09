# Feature Specification: Extract PDF Figures for Zotero Annotations

**Feature Branch**: `013-pdf-figure-extract`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "I have export of annotation from
zotero in @tmp/building-evolutionary-architectures. this time
the directory with annotations contains the corresponding PDF
file. when annotation references a figure from the text, i want
this figure to be extracted (screenshot) from the PDF file,
stored alongside the annotation and linked into it."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Figures from Caption Annotations (Priority: P1)

As a user who highlights figure captions in a book, I want the
corresponding figure screenshot extracted from the PDF and saved
alongside the annotation markdown file with an embedded image
link, so I can see the figure when reviewing my notes.

**Why this priority**: Figure-caption annotations (e.g., text
starting with "Figure 5-2.") are the most direct and unambiguous
references. The annotation's page number tells us exactly where
the figure is in the PDF.

**Independent Test**: Parse Zotero annotations from a directory
containing `Annotations.md`, `book.txt`, and a `.pdf` file. For
each annotation whose text starts with a figure caption pattern,
extract a screenshot of the figure region from the PDF page,
save it to an `images/` subdirectory, and embed an image link in
the annotation markdown.

**Acceptance Scenarios**:

1. **Given** a Zotero export directory containing `book.txt`,
   `Annotations.md`, and a `.pdf` file, **When** the parser
   encounters an annotation whose text starts with "Figure X-Y.",
   **Then** a screenshot of the corresponding PDF page is
   extracted, saved as an image file in the output directory, and
   the annotation markdown includes an image link.
2. **Given** a figure-caption annotation with page number,
   **When** the figure image is extracted, **Then** the image
   file is named using a predictable convention (e.g.,
   `figure-5-2.png`) and placed in an `images/` subdirectory.
3. **Given** a figure-caption annotation, **When** no PDF is
   present in the directory, **Then** the annotation is saved
   normally without an image link (backward compatibility).

---

### User Story 2 - Extract Figures Referenced Inline (Priority: P2)

As a user who highlights passages that mention figures inline
(e.g., "...as illustrated in Figure 2-1"), I want the
referenced figure screenshot extracted and linked in the
annotation so I can see the figure alongside the highlighted
text.

**Why this priority**: Inline figure references are common but
the figure may be on a different page than the annotation. The
page number in the annotation text gives a starting point, but
the actual figure page may differ.

**Independent Test**: Parse an annotation with an inline figure
reference. Verify the system attempts to find and extract the
figure from the PDF.

**Acceptance Scenarios**:

1. **Given** an annotation mentioning "Figure X-Y" inline,
   **When** the parser processes it, **Then** the system
   searches the PDF for the figure and extracts a screenshot
   if found.
2. **Given** an annotation with an inline reference where the
   figure is on a different page, **When** the system searches,
   **Then** it looks on the annotation's page and nearby pages
   to find the figure.

---

### User Story 3 - Graceful Fallback Without PDF (Priority: P2)

As a user who may not always have the PDF alongside the Zotero
export, I want the parser to work normally without figure
extraction so existing workflows are not disrupted.

**Why this priority**: Backward compatibility with the existing
Zotero parser is essential. The PDF is optional.

**Independent Test**: Run the parser on a Zotero export
directory that has no PDF. Verify output is identical to the
current behavior.

**Acceptance Scenarios**:

1. **Given** a Zotero export directory without a PDF file,
   **When** the parser is invoked, **Then** annotations are
   parsed and saved normally with no figure extraction and no
   errors.

---

### Edge Cases

- What happens when the PDF page contains multiple figures?
  The system should extract the figure whose caption matches
  the referenced figure number.
- What happens when the annotation references a figure that
  cannot be found in the PDF? The annotation is saved normally
  and a warning is emitted to stderr.
- What happens when the PDF file is corrupted or password-
  protected? The system should warn and proceed without figure
  extraction.
- How are figure numbers formatted? Zotero annotations use
  "Figure X-Y" (with hyphen), e.g., "Figure 2-1", "Figure
  5-17". Both caption and inline patterns should be detected.
- What happens with user notes like "Get the figure 5-2" that
  appear as standalone annotations? These should also trigger
  figure extraction from the referenced page.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect the presence of a `.pdf` file
  in the Zotero export directory and, when present, enable
  figure extraction during annotation parsing.
- **FR-002**: System MUST identify annotations that are figure
  captions by matching text that starts with a pattern like
  "Figure X-Y." (e.g., "Figure 5-2. Monolithic architectures
  always have a quantum of one").
- **FR-003**: System MUST identify inline figure references
  within annotation text by matching patterns like "Figure X-Y"
  (e.g., "as illustrated in Figure 2-1").
- **FR-004**: System MUST identify user notes requesting figure
  extraction, such as annotations containing "Get the figure
  X-Y" or similar explicit requests.
- **FR-005**: For each identified figure reference, the system
  MUST extract the figure image directly from the PDF page
  resources and save it to an `images/` subdirectory within
  the annotation output directory.
- **FR-006**: System MUST use the page number from the
  annotation metadata to locate the correct PDF page for
  figure extraction.
- **FR-007**: System MUST embed an image link (e.g.,
  `![Figure 5-2](images/figure-5-2.png)`) in the annotation
  markdown file for each extracted figure.
- **FR-008**: System MUST continue processing normally when
  no PDF is present in the directory — figure extraction is
  optional.
- **FR-009**: System MUST emit a warning to stderr when a
  figure reference is found but the figure cannot be extracted
  from the PDF.
- **FR-010**: System MUST handle corrupted or unreadable PDF
  files gracefully by emitting a warning and proceeding
  without figure extraction.
- **FR-011**: Image files MUST be named using a normalized
  convention (e.g., `figure-5-2.png`) regardless of the figure
  numbering style in the source text.

### Key Entities

- **Annotation**: Extended with optional figure references
  (reuses the existing `FigureRef` dataclass from the EPUB
  feature).
- **PDF**: A book file from which figure screenshots are
  extracted by rendering specific pages.
- **Figure Reference**: A detected mention of a figure in
  annotation text, either as a caption ("Figure 5-2."), inline
  reference ("Figure 2-1"), or explicit extraction request
  ("Get the figure 5-17").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All figure-caption annotations in the sample
  Zotero export produce annotation markdown files that include
  a visible image link to an extracted screenshot.
- **SC-002**: Extracted screenshots are viewable — they are
  valid image files that render correctly when opened.
- **SC-003**: The parser produces identical output to the
  existing Zotero parser when no PDF is present in the
  directory (full backward compatibility).
- **SC-004**: Warnings are emitted for any figure reference
  that cannot be extracted, with zero unhandled errors.
- **SC-005**: The sample export in
  `tmp/building-evolutionary-architectures/` produces figure
  screenshots for at least the figure-caption annotations.

## Assumptions

- The PDF file is located in the same directory as the Zotero
  export (`book.txt` and `Annotations.md`).
- There is at most one `.pdf` file per export directory.
- Figure references in Zotero annotations use the format
  "Figure X-Y" (hyphen-separated chapter and figure number),
  matching the O'Reilly style observed in the sample data.
- The page number in each Zotero annotation (e.g., "p. 26")
  corresponds to the physical PDF page where the figure can
  be found (or is nearby).
- PDF figures are embedded as images (typically JPEG) in the
  PDF page resources and can be extracted directly — no page
  rendering needed. When a page has multiple images, the
  largest by byte size is selected as the figure.
- A PDF reading library (`pypdf`, pure Python) will be needed
  as a new dependency (this is a deliberate exception to
  Constitution Principle V, justified by the fact that PDF
  parsing cannot be done with stdlib alone).

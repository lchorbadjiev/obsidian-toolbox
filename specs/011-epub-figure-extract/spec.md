# Feature Specification: Extract EPUB Figures for Annotations

**Feature Branch**: `011-epub-figure-extract`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "Now I have a Boox annotations
exported in @tmp/the-power-of-creative-destruction/ together
with the EPUB book. If an annotation mentions a figure from the
book I want it saved alongside the annotation and linked inside
the annotation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Figures for Figure-Caption Annotations (Priority: P1)

As a user who highlights figure captions on a Boox e-reader, I
want the corresponding figure image extracted from the EPUB and
saved alongside the annotation markdown file, with a link to the
image embedded in the annotation, so I can see the figure when
reviewing my notes.

**Why this priority**: Figure-caption annotations (e.g., text
starting with "FIGURE 2.1.") are the most direct and
unambiguous references to figures. They form the core use case.

**Independent Test**: Parse annotations from a Boox export
directory that also contains an EPUB. For each annotation whose
text starts with a figure caption pattern (e.g., "FIGURE 2.1."),
extract the matching image from the EPUB, save it to the output
directory, and embed an image link in the annotation markdown.

**Acceptance Scenarios**:

1. **Given** a Boox export directory containing `book.txt`, an
   annotation `.txt` file, and an `.epub` file, **When** the
   parser encounters an annotation whose text starts with
   "FIGURE X.Y.", **Then** the corresponding image is extracted
   from the EPUB, saved as a file in the output directory, and
   the annotation markdown includes an image link to it.
2. **Given** a figure-caption annotation, **When** the figure
   image is successfully extracted, **Then** the image file is
   named using a predictable convention (e.g.,
   `figure-2-1.jpg`) and placed in an `images/` subdirectory
   of the output directory.
3. **Given** a figure-caption annotation, **When** no matching
   image is found in the EPUB, **Then** the annotation is
   still saved normally without an image link, and a warning
   is emitted.

---

### User Story 2 - Extract Figures Referenced Inline (Priority: P2)

As a user who highlights passages that mention figures inline
(e.g., "...population in Europe (Figure 2.3)..."), I want the
referenced figure image extracted and linked in the annotation
so I can see the figure in context with the highlighted text.

**Why this priority**: Inline figure references are common but
require pattern matching within the annotation text. They
complement the caption-based extraction.

**Independent Test**: Parse an annotation whose text contains
"(Figure X.Y)" or "Figure X.Y" mid-sentence. Verify the
referenced figure is extracted and linked.

**Acceptance Scenarios**:

1. **Given** an annotation whose text contains an inline
   figure reference like "(Figure 2.3)" or "Figure 3.5",
   **When** the parser processes it, **Then** the referenced
   figure image is extracted from the EPUB and an image link
   is appended to the annotation markdown.
2. **Given** an annotation with multiple inline figure
   references, **When** the parser processes it, **Then** all
   referenced figures are extracted and linked.

---

### User Story 3 - Graceful Fallback Without EPUB (Priority: P2)

As a user who may not always have the EPUB alongside the
export, I want the parser to work normally without figure
extraction when no EPUB is present, so existing workflows
are not disrupted.

**Why this priority**: Backward compatibility with the existing
Boox parser is essential. The EPUB is optional.

**Independent Test**: Run the parser on a Boox export directory
that has no EPUB file. Verify all annotations are parsed
normally with no errors.

**Acceptance Scenarios**:

1. **Given** a Boox export directory without an EPUB file,
   **When** the parser is invoked, **Then** annotations are
   parsed normally with no figure extraction and no errors.

---

### Edge Cases

- What happens when the EPUB contains multiple image files
  that could match a figure reference? The system should use
  the XHTML-derived figure-id-to-image mapping to select the
  correct image.
- What happens when the annotation references a figure that
  does not exist in the EPUB? The annotation is saved normally
  and a warning is emitted to stderr.
- What happens when the EPUB file is corrupted or unreadable?
  The system should warn and proceed without figure extraction,
  not fail entirely.
- How are multi-part figures handled (e.g., "Figure 7.9b")?
  The system should match the base figure number and extract
  the corresponding image variant if available.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect the presence of an `.epub`
  file in the Boox export directory and, when present, enable
  figure extraction during annotation parsing.
- **FR-002**: System MUST identify annotations that are
  figure captions by matching text that starts with a pattern
  like "FIGURE X.Y." (case-insensitive).
- **FR-003**: System MUST identify inline figure references
  within annotation text by matching patterns like
  "(Figure X.Y)" or "Figure X.Y" followed by punctuation or
  end of sentence.
- **FR-004**: For each identified figure reference, the system
  MUST locate the corresponding image file inside the EPUB by
  parsing the EPUB's XHTML content to build a figure-id-to-image
  mapping (e.g., finding `<figure>` or `<a id="fig2-1"/>`
  elements and their associated `<img>` tags). This approach
  works regardless of the EPUB's image naming convention.
- **FR-005**: System MUST extract matched images from the EPUB
  and save them to an `images/` subdirectory within the
  annotation output directory.
- **FR-006**: System MUST embed an image link (e.g.,
  `![Figure 2.1](images/figure-2-1.jpg)`) in the annotation
  markdown file for each extracted figure.
- **FR-007**: System MUST continue processing normally when
  no EPUB is present in the directory — figure extraction is
  optional.
- **FR-008**: System MUST emit a warning to stderr when a
  figure reference is found but the corresponding image cannot
  be located in the EPUB.
- **FR-009**: System MUST handle corrupted or unreadable EPUB
  files gracefully by emitting a warning and proceeding
  without figure extraction.
- **FR-010**: Image files MUST be named using a normalized
  convention (e.g., `figure-2-1.jpg`) regardless of the
  original filename inside the EPUB.

### Key Entities

- **Annotation**: Extended with optional image link(s) when
  figures are detected.
- **EPUB**: A ZIP-based book file containing chapter XHTML and
  image assets. Image naming conventions vary across publishers
  (e.g., `ch2_fig1.jpg`, `00002.jpeg`). The XHTML content
  provides the authoritative mapping from figure IDs to image
  files.
- **Figure Reference**: A detected mention of a figure in
  annotation text, either as a caption ("FIGURE 2.1.") or
  inline reference ("Figure 2.3").

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All figure-caption annotations in the sample
  export produce annotation markdown files that include a
  visible image link.
- **SC-002**: All inline figure references in the sample
  export produce annotation markdown files that include the
  referenced figure image.
- **SC-003**: Extracted images are viewable — they are valid
  image files that render correctly when opened.
- **SC-004**: The parser produces identical output to the
  existing Boox parser when no EPUB is present in the
  directory (full backward compatibility).
- **SC-005**: Warnings are emitted for any figure reference
  that cannot be matched to an EPUB image, with zero
  unhandled errors.

## Clarifications

### Session 2026-04-09

- Q: How should the system map figure references to EPUB images
  when filenames don't encode chapter/figure numbers? → A: Parse
  EPUB XHTML to find figure-id-to-image mappings (works for all
  EPUBs regardless of image naming convention).

## Assumptions

- The EPUB file is located in the same directory as the
  Boox export (`book.txt` and annotation `.txt` file).
- There is at most one `.epub` file per export directory.
- Image naming conventions vary across EPUB publishers (e.g.,
  `ch2_fig1.jpg`, `00002.jpeg`). The system parses EPUB
  XHTML content to build figure-id-to-image mappings rather
  than relying on filename conventions.
- Figure references in annotations follow the pattern
  "FIGURE X.Y." (captions) or "Figure X.Y" (inline), where
  X is the chapter number and Y is the figure number within
  the chapter.
- The EPUB uses standard ZIP compression and can be read as
  a ZIP archive.
- EPUB XHTML files contain `<figure>` elements or anchor
  tags with figure IDs (e.g., `id="fig2-1"`) that reference
  `<img>` tags pointing to the actual image files.

# Feature Specification: Merge Split Zotero Annotations

**Feature Branch**: `014-merge-split-annotations`
**Created**: 2026-04-09
**Status**: Draft
**Input**: User description: "Zotero does not allow highlighting
across pages, so annotations that span page boundaries get split
into two separate entries. The parser should detect and merge
these using PDF text proximity."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Merge Adjacent-Page Annotation Pairs (Priority: P1)

As a user who highlights passages that span page boundaries in
Zotero, I want the parser to automatically detect and merge
split annotations into a single annotation so that my notes
accurately represent the original highlighted passage.

**Why this priority**: Split annotations produce fragmented
notes that lose context. The quote ending on p.18 and the
attribution "—Donella H. Meadows" on p.19 should be a single
annotation with the full quote and attribution.

**Independent Test**: Parse Zotero annotations from a directory
containing a PDF. Verify that consecutive annotations on
adjacent pages whose texts appear close together in the PDF are
merged into a single annotation.

**Acceptance Scenarios**:

1. **Given** two consecutive Zotero annotations on pages N and
   N+1, **When** the PDF text confirms the two highlighted
   passages are adjacent (within a few characters of each other
   in the page text), **Then** the parser merges them into a
   single annotation with concatenated text, using the first
   annotation's page number.
2. **Given** two consecutive annotations on adjacent pages,
   **When** the PDF text shows they are far apart (different
   sections of the page), **Then** the parser keeps them as
   separate annotations.
3. **Given** a merge occurs, **When** the merged annotation is
   saved, **Then** the title is regenerated from the combined
   text.

---

### User Story 2 - Graceful Fallback Without PDF (Priority: P2)

As a user who may not have the PDF alongside the Zotero export,
I want the parser to skip merge detection and produce the same
output as before so existing workflows are not disrupted.

**Why this priority**: Backward compatibility. Merge detection
requires a PDF for text verification.

**Independent Test**: Run the parser on a Zotero export without
a PDF. Verify output is identical to the current behavior.

**Acceptance Scenarios**:

1. **Given** a Zotero export directory without a PDF, **When**
   the parser is invoked, **Then** no merging occurs and all
   annotations are output individually (same as before).

---

### Edge Cases

- What happens when three or more consecutive annotations
  should be merged (e.g., a long passage spanning 3 pages)?
  The system should merge all of them into one.
- What happens when two annotations are on adjacent pages but
  the text is not adjacent in the PDF? They should remain
  separate.
- What happens when the PDF text extraction fails for a page?
  The system should skip merge detection for that pair and
  keep them separate.
- How is "close" defined? The end of the first annotation's
  text and the start of the second annotation's text should
  appear within approximately 10 characters of each other in
  the extracted PDF page text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect candidate merge pairs:
  consecutive annotations on adjacent pages (page N and page
  N+1).
- **FR-002**: When a PDF is present, the system MUST extract
  text from the relevant PDF pages and check whether the two
  annotation texts appear near each other in the page content.
- **FR-003**: System MUST merge candidate pairs whose texts
  are adjacent in the PDF (within ~10 characters proximity)
  by concatenating the second annotation's text onto the first,
  separated by a space.
- **FR-004**: The merged annotation MUST use the first
  annotation's page number and metadata.
- **FR-005**: The merged annotation's title MUST be
  regenerated from the combined text.
- **FR-006**: System MUST support chained merges — if
  annotations A (p.N), B (p.N+1), and C (p.N+2) are all
  adjacent, all three should merge into one.
- **FR-007**: System MUST NOT merge annotations when no PDF
  is present (backward compatibility).
- **FR-008**: System MUST NOT merge annotations that are on
  adjacent pages but whose texts are not adjacent in the PDF
  content.
- **FR-009**: System MUST handle PDF text extraction failures
  gracefully — skip merge detection for affected pairs and
  keep them separate.

### Key Entities

- **Annotation**: The existing annotation dataclass. Merged
  annotations have concatenated text and the first
  annotation's page/metadata.
- **Merge Candidate**: A pair of consecutive annotations on
  adjacent pages that may need merging.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The known split annotation pair (p.18 "Multiple
  Architectural Dimensions..." + p.19 "—Donella H. Meadows")
  in the sample export is merged into a single annotation.
- **SC-002**: Independent annotations that happen to be on
  adjacent pages remain separate (no false merges).
- **SC-003**: The total annotation count decreases by the
  number of merges performed (verifiable against expected
  count).
- **SC-004**: The parser produces identical output when no PDF
  is present (full backward compatibility).

## Assumptions

- Merge detection requires a PDF file in the export directory.
  Without a PDF, the feature is disabled.
- "Adjacent in PDF text" means the tail of the first
  annotation's text and the head of the second annotation's
  text appear within approximately 10 characters of each
  other in the extracted page text (using substring search).
- The Zotero annotation color field is not currently available
  in the parsed data (Zotero exports in `Annotations.md`
  don't include color), so color matching is deferred. The
  proximity check alone is sufficient for merge detection.
- Merge detection runs after initial annotation parsing but
  before figure extraction and numbering.

# Feature Specification: Fix Zotero Word Concatenation

**Feature Branch**: `007-fix-zotero-word-concat`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "The annotation exports from zotero
has very nasty concatenation of words as isthat, includesnetwork,
muchcomplexity, adaptingit, etc. Can we use aspell to detect such
issues and fix them?"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Automatic Word Splitting During Parse (Priority: P1)

As a user parsing Zotero annotation exports, I want
concatenated words (e.g., "isthat", "includesnetwork",
"SoftwareWithout") to be automatically detected and split
into proper words so that the resulting annotation text is
readable without manual editing.

**Why this priority**: This is the core problem. Zotero's PDF
annotation export frequently drops spaces between words,
producing unreadable text. Without this fix, every annotation
requires manual correction.

**Independent Test**: Run `otb zotero parse` on the existing
fixture directory and verify that known concatenated words in
the output are split correctly (e.g., "isthat" becomes
"is that", "SoftwareWithout" becomes "Software Without").

**Acceptance Scenarios**:

1. **Given** an Annotations.md file containing "isthat",
   **When** the user runs the Zotero parser, **Then** the
   output annotation text contains "is that".
2. **Given** an annotation with "SoftwareWithout refactoring",
   **When** parsed, **Then** the output reads "Software
   Without refactoring".
3. **Given** an annotation with no concatenation issues,
   **When** parsed, **Then** the text is unchanged.
4. **Given** a legitimate compound word or proper noun (e.g.,
   "JavaScript", "without"), **When** parsed, **Then** the
   word is preserved unchanged.

---

### User Story 2 — Review Mode for Splits (Priority: P2)

As a user, I want to see what word splits were performed so
I can verify correctness, especially for domain-specific
terms that the dictionary might not recognize.

**Why this priority**: Automated splitting will occasionally
make mistakes on technical jargon or proper nouns. Users need
visibility into what changed.

**Independent Test**: Run the parser with a verbose flag and
verify it reports which words were split and how.

**Acceptance Scenarios**:

1. **Given** the user runs the parser, **When** word splits
   occur, **Then** the tool prints a summary count of splits
   performed to stderr (e.g., "Fixed 12 concatenated words").
2. **Given** the user runs with a verbose flag, **When**
   splits occur, **Then** each split is reported individually
   to stderr (e.g., "'SoftwareWithout' → 'Software
   Without'").

---

### Edge Cases

- What happens when aspell is not installed on the system?
  The tool MUST report a clear error message and exit
  gracefully rather than crashing.
- What happens with words that are legitimately concatenated
  in English (e.g., "cannot", "without", "into", "himself")?
  These MUST NOT be split.
- What happens with proper nouns that aspell does not
  recognize (e.g., "CunninghamWard")? The tool should
  attempt a split based on uppercase boundaries as a
  secondary heuristic.
- What happens with very short words? Words shorter than
  4 characters should not be candidates for splitting to
  avoid false positives.
- What happens when multiple valid splits exist for a
  concatenated string? The tool should prefer the split
  where both resulting words are recognized by the
  dictionary.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST detect concatenated words in Zotero
  annotation text using aspell as a spellcheck backend.
- **FR-002**: System MUST split detected concatenated words
  by finding a split point where both halves are valid
  dictionary words according to aspell.
- **FR-003**: System MUST handle mixed-case concatenation
  patterns (e.g., "SoftwareWithout" where an uppercase letter
  signals the start of a new word).
- **FR-004**: System MUST preserve legitimate English compound
  words and contractions (e.g., "cannot", "without", "into",
  "himself", "refactoring").
- **FR-005**: System MUST preserve recognized proper nouns
  and technical terms (e.g., "JavaScript", "GitHub").
- **FR-006**: System MUST apply word-splitting as part of the
  existing Zotero annotation parsing pipeline so that text is
  clean when written to output files.
- **FR-007**: System MUST report an actionable error message
  and exit with a non-zero code if aspell is not available.
- **FR-008**: System MUST print a count of fixed
  concatenations to stderr after parsing completes.
- **FR-009**: System MUST support a verbose mode that logs
  each individual word split performed.
- **FR-010**: System MUST not modify words that are already
  valid dictionary words, even if they could theoretically be
  split into two words.

### Key Entities

- **ConcatenatedWord**: A token in annotation text that is
  not recognized by the dictionary and can be split into two
  recognized words. Attributes: original text, split result,
  source annotation context.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of concatenated words in the test
  fixture are correctly split without manual intervention.
- **SC-002**: Zero false positives on legitimate English
  words — no valid dictionary words are incorrectly split.
- **SC-003**: The word-splitting step adds no more than
  2 seconds of processing time for a 300-annotation export.
- **SC-004**: Users can parse a Zotero export and get
  readable annotation text in a single command without any
  post-processing.

## Assumptions

- aspell is available as a system-level command-line tool
  (installed via Homebrew on macOS, apt on Linux).
- The aspell English dictionary is sufficient for detecting
  valid English words; domain-specific dictionaries are out
  of scope for v1.
- Word concatenation errors in Zotero exports are caused by
  PDF text extraction dropping spaces, producing patterns
  like lowercase-to-uppercase boundaries and dictionary-word
  pairs that are not themselves dictionary words.
- The splitting algorithm only needs to handle two-word
  concatenations (e.g., "isthat" → "is that"). Three-way
  splits are rare enough to be out of scope for v1.
- The existing Zotero parser fixture
  (`tests/fixtures/zotero/Annotations.md`) contains
  representative examples of the concatenation problem.

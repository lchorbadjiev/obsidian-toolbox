# Feature Specification: Export Book Annotations to Anki

**Feature Branch**: `005-anki-cards-export`
**Created**: 2026-04-06
**Status**: Draft
**Input**: User description: "I need a command, that loads annotations of a book
and puts it into a deck of Anki cards using the Anki REST API."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Annotations to Anki Deck (Priority: P1)

A user has a directory of annotation markdown files for a book and wants to
send all annotations to Anki as flashcards. They run a single command
specifying the directory, and all annotations are sent to a corresponding
Anki deck ready for review. Each exported annotation's markdown file is
updated with the Anki note ID so future runs can skip it.

**Why this priority**: This is the core feature — without it, nothing else is
useful. Delivering this alone provides the full end-to-end value of the feature.

**Independent Test**: Run the command pointing to a fixture annotation
directory. Verify the correct number of cards appears in Anki under the
expected deck name, and that each markdown file's frontmatter contains an
`anki_id` field set to the corresponding note ID.

**Acceptance Scenarios**:

1. **Given** a directory of annotation markdown files for a book, **When** the
   user runs `otb anki export <path>`, **Then** all annotations are created as
   cards in an Anki deck named after the book, the command prints a summary of
   how many cards were created, and each markdown file is updated with the
   returned Anki note ID in the `anki_id` frontmatter field.
2. **Given** Anki is not running (AnkiConnect unreachable), **When** the user
   runs the command, **Then** the command exits with a clear error message
   indicating that Anki must be open with AnkiConnect installed.

---

### User Story 2 - Specify Target Deck Name (Priority: P2)

A user wants to send annotations to a custom-named Anki deck (e.g., to
organise cards under a subject area rather than by book title).

**Why this priority**: Deck organisation is a key part of the Anki workflow.
Users often maintain structured deck hierarchies (e.g., `Books::Non-Fiction`).
Without this option, they must rename or move cards manually after import.

**Independent Test**: Run the command with an explicit `--deck` option. Verify
in Anki that the cards appear under the specified deck name, not the default
book-title deck.

**Acceptance Scenarios**:

1. **Given** an annotation directory and `--deck "Non-Fiction::History"`,
   **When** the user runs the command, **Then** cards are created in the
   specified deck, including nested deck creation if the deck does not yet
   exist.

---

### User Story 3 - Skip Already-Exported Annotations (Priority: P3)

A user runs the export command more than once (e.g., after adding new
annotations). Annotations whose markdown file already has an `anki_id` are
skipped — only new annotations are sent to Anki.

**Why this priority**: Re-running the command on a partially-exported book is a
natural workflow. Without `anki_id`-based skip detection, users accumulate
redundant cards.

**Independent Test**: Export a set of annotations, confirm `anki_id` is set in
each markdown file, then run the command again. Confirm the card count in Anki
does not increase and the command reports all cards as skipped.

**Acceptance Scenarios**:

1. **Given** annotation markdown files already have `anki_id` set (from a
   previous export), **When** the user runs the command again, **Then**
   those annotations are skipped and the summary reports the number skipped
   vs. created.

---

### Edge Cases

- What happens when the annotation directory is empty (no `.md` files found)?
- What happens when Anki is running but AnkiConnect is not installed or the
  port is non-default?
- What happens when an annotation has only whitespace text?
- What happens when the book title contains characters that Anki interprets as
  deck hierarchy separators (`::`)?
- What happens when AnkiConnect returns an error for a subset of cards (partial
  failure)?
- If `anki_id` is set but the note no longer exists in Anki (card was
  deleted), the command re-creates the card and overwrites `anki_id` with the
  new note ID.
- If the `anki_id` write-back fails (e.g., file is read-only), the card
  still counts as "created" and a warning is printed to stderr with the
  affected file path. The next run will re-create the card (duplicate in
  Anki) unless the user fixes the file permissions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The command MUST accept a path argument pointing to a directory
  of annotation markdown files. Non-directory paths MUST be rejected with a
  clear error message.
- **FR-002**: The command MUST parse the directory using `parse_annotation_dir`
  and produce a list of `Annotation` objects including the `anki_id` field
  from each file's frontmatter.
- **FR-003**: The command MUST create an Anki deck named after the book title
  if no `--deck` option is provided, creating the deck automatically if it does
  not exist.
- **FR-004**: Users MUST be able to override the target deck name with a
  `--deck <name>` option, supporting Anki's nested deck syntax
  (`Parent::Child`).
- **FR-005**: Each annotation MUST be exported as one Anki card with two
  fields: a front field containing the annotation's context (chapter and title)
  and a back field containing the annotation's full text.
- **FR-006**: The command MUST skip an annotation whose `anki_id` frontmatter
  field is non-null, after verifying that note still exists in Anki. If the
  note has been deleted, the card is re-created and `anki_id` is overwritten.
- **FR-007**: After successfully creating a card in Anki, the command MUST
  attempt to write the returned Anki note ID back to the annotation's markdown
  file as the `anki_id` frontmatter field. If the write fails, the card is
  still counted as "created" and a warning MUST be emitted to stderr
  identifying the affected file.
- **FR-008**: The command MUST communicate with Anki via AnkiConnect, the
  standard local REST interface, running on `localhost:8765` by default.
- **FR-009**: Users MUST be able to override the AnkiConnect URL with an
  `--anki-url` option for non-default ports or remote setups.
- **FR-010**: The command MUST print a completion summary indicating how many
  cards were created, how many were skipped, and how many failed.
- **FR-011**: The command MUST exit with a non-zero status code and a
  human-readable error message if Anki is unreachable.
- **FR-012**: The command MUST skip annotations with empty or whitespace-only
  text and report the count of skipped items in the summary.

### Key Entities

- **Annotation**: Existing dataclass extended with an optional `anki_id: int |
  None` field. Set to the Anki note ID after a successful export; `None` until
  then. Fields: `book`, `chapter`, `page`, `location`, `text`, `title`,
  `color`, `anki_id`.
- **Anki Card**: A two-sided flashcard. Front holds context (chapter + title);
  back holds the full annotation text.
- **Anki Deck**: A named collection of cards in Anki. Created automatically if
  it does not exist. Name defaults to the book title.
- **AnkiConnect**: The local REST API addon for Anki. The interface between the
  command and Anki's data store.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can export an entire book's annotations to Anki in a
  single command invocation, without any manual copy-paste.
- **SC-002**: Running the command twice on the same source produces no
  duplicate cards in Anki; the second run reports all cards as skipped.
- **SC-003**: The command completes export of 100 annotations in under
  10 seconds under normal conditions.
- **SC-004**: The command produces a clear, actionable error message for every
  known failure mode (Anki not running, empty directory, invalid path), with a
  zero rate of silent failures.
- **SC-005**: 100% of non-empty, non-skipped annotations are represented as
  cards in Anki and have `anki_id` written to their markdown file after a
  successful export.

## Clarifications

### Session 2026-04-06

- Q: Should `anki_id` in frontmatter be the primary skip mechanism for
  markdown sources, with `anki_id` written back after successful creation?
  → A: Yes — `anki_id` is the skip mechanism; written back after creation.
- Q: What should happen when `anki_id` is set but the note no longer exists
  in Anki (e.g., card was deleted)? → A: Re-create the card and overwrite
  `anki_id` with the new note ID.
- Q: Should the command support Kindle HTML files as input sources?
  → A: No — export to Anki always starts from markdown annotation directories
  only.
- Q: What should happen if the `anki_id` write-back to the markdown file
  fails (e.g., file is read-only)? → A: Count as "created" (the card exists
  in Anki); emit a stderr warning with the affected file path so the user is
  aware the ID was not persisted.

## Assumptions

- AnkiConnect (Anki addon 2055492823) is installed in the user's Anki
  application; the command does not install or configure Anki addons.
- Anki must be open and running during export; the command does not launch
  Anki.
- The default AnkiConnect port is `8765` on `localhost`.
- Each annotation maps to exactly one Anki card; multi-card generation per
  annotation (e.g., cloze deletions) is out of scope for v1.
- The Anki note type used for cards is the built-in "Basic" type with "Front"
  and "Back" fields; custom note type selection is out of scope for v1.
- Duplicate detection is `anki_id`-first: an annotation with a non-null
  `anki_id` is skipped after verifying the note still exists in Anki.
- The `color` field of annotations is not used in card content for v1 (tag
  support by colour is a potential future enhancement).
- The command is invoked locally; no network authentication beyond
  AnkiConnect's local-only access model is required.

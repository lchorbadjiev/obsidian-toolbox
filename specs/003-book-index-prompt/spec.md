# Feature Specification: Book Index Generation Prompt

**Feature Branch**: `003-book-index-prompt`  
**Created**: 2026-04-05  
**Status**: Draft  
**Input**: User description: "I want to have a prompt in the MCP server that helps generate an index file with a summary about the book itself similar to the one in tmp/The Invention of Science - Index.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Book Index via MCP Prompt (Priority: P1)

A user asks their AI assistant to create a book index file for a set of highlights they have
saved in a directory. The assistant calls the MCP prompt with the highlights directory, receives
a structured prompt with all the highlight data, and uses it to generate a complete index
markdown file. The index includes the book's frontmatter metadata, a prose summary of the
book's argument and themes, and a chapter-by-chapter list of links to each individual note.

**Why this priority**: This is the core value of the feature — turning a flat collection of
highlights into a navigable, summarized index document. It requires no other stories to deliver
value.

**Independent Test**: Call the MCP prompt with `tests/fixtures/highlights/` (4 highlights);
verify the prompt returns messages that include the book title, author, all highlight texts,
and chapter groupings. Provide the returned messages to an LLM and verify the generated
index contains frontmatter (author, tags, published year), a prose summary paragraph, and a
"Notes by Chapter" section with one subsection per chapter listing note links.

**Acceptance Scenarios**:

1. **Given** a directory of highlight markdown files for one book, **When** the agent calls
   the MCP prompt with that directory, **Then** the prompt returns context messages that
   include all the highlight data and instructions sufficient to generate an index file
   matching the example format.

2. **Given** the prompt output, **When** the LLM generates the index, **Then** the result
   includes: YAML frontmatter with author, published year, and tags; a prose summary paragraph
   covering the book's main argument and themes; a "Notes by Chapter" section with subsections
   named after each chapter; and each note listed as a wikilink using the highlight filename
   (without extension) as the link text.

3. **Given** a directory containing highlights from multiple chapters, **When** the index is
   generated, **Then** the notes are grouped under their respective chapter headings in
   filename-sorted order within each chapter.

4. **Given** a non-existent directory path, **When** the prompt is called, **Then** an error
   is returned without crashing.

5. **Given** an empty directory, **When** the prompt is called, **Then** an informative error
   or empty-state response is returned.

---

### Edge Cases

- What happens when highlights from only one chapter are present?
- What if highlight files are missing the chapter field?
- What if the directory contains a mix of well-formed and malformed files — are partial results
  still included?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The MCP server MUST expose a prompt named `generate_book_index` that accepts a
  `directory` argument (path to a folder of highlight markdown files).

- **FR-002**: The prompt MUST read all valid highlight markdown files from the given directory
  and include their content — book title, author, chapter, text, number, page, and location —
  as context in the returned messages.

- **FR-003**: The prompt MUST include instructions that guide the LLM to produce an index file
  with: (a) YAML frontmatter containing at minimum `author`, `published` year (if available),
  and a `tags` list; (b) an H1 heading with the full book title; (c) a prose summary of the
  book; (d) a "Notes by Chapter" section with one H3 subsection per chapter containing
  wikilinks to individual note files.

- **FR-004**: Wikilinks in the generated index MUST use the path format
  `[[notes/NNN - Title of Note]]` where `NNN` matches the highlight number and "Title of Note"
  matches the highlight title, consistent with the filename convention used by `save_highlights`.

- **FR-005**: The prompt MUST group notes under their corresponding chapter headings, in
  filename-sorted order within each chapter.

- **FR-006**: If the directory does not exist or is not a directory, the prompt MUST return an
  error message rather than raising an unhandled exception visible to the caller.

- **FR-007**: If the directory contains no valid highlight files, the prompt MUST return an
  informative message indicating there is nothing to index.

- **FR-008**: Malformed highlight files encountered while reading the directory MUST be skipped
  and reported in the prompt context rather than aborting the entire prompt.

### Key Entities

- **Book Index**: A markdown document representing a single book, containing metadata
  (author, year, tags), a prose summary, and an organized list of note links grouped by
  chapter.

- **Note Link**: A wikilink entry in the index pointing to an individual highlight file,
  following the format `[[notes/NNN - Title]]`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given a directory of 4 or more highlights, the generated index includes all
  highlights organized under the correct chapter headings with no highlights omitted.

- **SC-002**: The generated index is a valid markdown file that can be saved and opened in
  Obsidian without errors (correct frontmatter syntax, valid wikilink format).

- **SC-003**: An agent can call the prompt and produce a complete, usable index file without
  additional guidance beyond the prompt output — zero manual post-processing required for
  well-formed input.

- **SC-004**: Malformed highlight files in the directory do not cause the prompt to fail;
  valid highlights are still included and any skipped files are reported.

## Assumptions

- Highlight files in the directory were written by `save_highlights` and follow the filename
  convention `NNN - Title of Note.md`; the note link format in the index is derived from
  this convention.
- All highlights in the directory belong to a single book; multi-book directories are out
  of scope.
- The `published` year in the index frontmatter is taken from highlight metadata if available;
  if not present in the highlights, the LLM is instructed to leave it blank or infer it.
- The prose book summary is generated by the host LLM from the highlight texts and titles;
  no external book database is queried.
- Saving the index file to disk is handled by the calling agent, not by this prompt.

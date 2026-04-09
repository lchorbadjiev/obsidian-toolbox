# Tasks: Extract EPUB Figures for Annotations

**Input**: Design documents from `/specs/011-epub-figure-extract/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/

**Organization**: Tasks are grouped by user story to enable
independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Phase 1: Setup

**Purpose**: Create test fixtures and shared data structures

- [x] T001 Create a minimal test EPUB fixture at
  `tests/fixtures/boox/test.epub` containing one XHTML file
  with two `<figure>` elements (Pattern A style with
  `<a id="fig1-1"/>`, `<img>`, and `<figcaption>` with
  "FIGURE 1.1." label) and two small placeholder JPEG images
  in `images/` directory
- [x] T002 Add `FigureRef` dataclass to `src/otb/parser.py`
  with fields `label: str` and `image_path: str`. Add
  optional `figures: list[FigureRef]` field to `Annotation`
  dataclass with `field(default_factory=list)`

**Checkpoint**: Fixture and data model ready for test-first
development

---

## Phase 2: Foundational — EPUB Figure Parsing

**Purpose**: Core EPUB parsing infrastructure that all user
stories depend on

### Tests for Foundational Phase

> **NOTE: Write these tests FIRST, ensure they FAIL before
> implementation (Constitution III)**

- [x] T003 [P] Write test `test_parse_epub_figures` in
  `tests/test_epub_figures.py` verifying that
  `parse_epub_figures(epub_path)` returns a dict mapping
  figure labels (e.g., "1.1") to image bytes for the test
  EPUB fixture
- [x] T004 [P] Write test `test_parse_epub_figures_missing`
  in `tests/test_epub_figures.py` verifying that
  `parse_epub_figures` on a nonexistent path returns an
  empty mapping (graceful failure)
- [x] T005 [P] Write test `test_detect_figure_refs_caption`
  in `tests/test_epub_figures.py` verifying that
  `detect_figure_refs("FIGURE 2.1. Per capita GDP...")` returns
  `["2.1"]`
- [x] T006 [P] Write test `test_detect_figure_refs_inline`
  in `tests/test_epub_figures.py` verifying that
  `detect_figure_refs("...Europe (Figure 2.3).3 This...")` returns
  `["2.3"]`
- [x] T007 [P] Write test `test_detect_figure_refs_multiple`
  in `tests/test_epub_figures.py` verifying that multiple
  inline references (e.g., "Figure 3.5" and "Figure 4.7")
  in one text return `["3.5", "4.7"]`
- [x] T008 [P] Write test `test_detect_figure_refs_none`
  in `tests/test_epub_figures.py` verifying that text with
  no figure references returns `[]`

### Implementation for Foundational Phase

- [x] T009 Create `src/otb/epub_figures.py` with:
  `parse_epub_figures(epub_path: Path) -> dict[str, tuple[bytes, str]]`
  that opens EPUB as ZIP, finds XHTML files, parses with
  BeautifulSoup, finds `<figure>` elements, extracts figure
  labels from `<figcaption>` text matching
  `FIGURE\s+(\d+\.\d+[a-z]?)`, reads associated `<img>` src
  image bytes from ZIP, returns dict of label → (bytes, ext).
  Handle missing/corrupt EPUB gracefully (return empty dict,
  warn to stderr).
- [x] T010 Add `detect_figure_refs(text: str) -> list[str]`
  to `src/otb/epub_figures.py` using regex to find caption
  pattern (`^FIGURE\s+(\d+\.\d+[a-z]?)`, case-insensitive)
  and inline pattern (`Figure\s+(\d+\.\d+[a-z]?)`)
- [x] T011 Run `uv run pytest tests/test_epub_figures.py`
  and verify all tests pass (green)
- [x] T012 Run `uv run mypy src/otb/epub_figures.py` and
  `uv run pylint src/otb/epub_figures.py` — fix any issues

**Checkpoint**: EPUB parsing and figure detection working
independently

---

## Phase 3: User Story 1 — Figure-Caption Annotations (Priority: P1)

**Goal**: Annotations starting with "FIGURE X.Y." get the
corresponding image extracted and linked.

**Independent Test**: Parse Boox fixture with test EPUB, verify
caption annotations get FigureRef objects attached and images
are written.

### Tests for User Story 1

- [x] T013 [P] [US1] Write test `test_boox_parse_with_epub`
  in `tests/test_epub_figures.py` that creates a temp dir
  with `book.txt`, an annotation file containing a
  "FIGURE 1.1." caption annotation, and the test EPUB fixture,
  then calls `parse_boox_annotations` and verifies the
  annotation has a `figures` list with one FigureRef
- [x] T014 [P] [US1] Write test
  `test_write_annotation_with_figure` in
  `tests/test_epub_figures.py` that creates an Annotation
  with a FigureRef, calls `write_annotation` with
  `figure_data` dict, and verifies the markdown contains
  `![Figure 1.1](images/figure-1-1.jpg)` and the image
  file exists in `output/images/`

### Implementation for User Story 1

- [x] T015 [US1] Modify `parse_boox_annotations` in
  `src/otb/boox_parser.py` to: detect `.epub` file in
  directory, call `parse_epub_figures` to get figure map,
  call `detect_figure_refs` on each annotation's text,
  attach matching `FigureRef` objects to annotations.
  Return the figure map alongside annotations for downstream
  image writing.
- [x] T016 [US1] Modify `write_annotation` in
  `src/otb/md_writer.py` to accept optional `figure_data:
  dict[str, tuple[bytes, str]]` parameter. When an
  annotation has figures and figure_data is provided:
  create `images/` subdirectory, write image bytes to
  `images/figure-{label}.{ext}`, append
  `![Figure {label}](images/figure-{label}.{ext})` after
  the blockquote text. Update `write_annotations` similarly.
- [x] T017 [US1] Modify `boox_parse` CLI command in
  `src/otb/cli.py` to pass figure data from
  `parse_boox_annotations` through to `write_annotations`
- [x] T018 [US1] Run `uv run pytest` and verify all tests pass
- [x] T019 [US1] Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix any issues

**Checkpoint**: Caption-based figure extraction working
end-to-end via CLI

---

## Phase 4: User Story 2 — Inline Figure References (Priority: P2)

**Goal**: Annotations mentioning "Figure X.Y" inline get the
referenced figure extracted and linked.

**Independent Test**: Parse an annotation with inline figure
reference, verify FigureRef attached and image linked.

### Tests for User Story 2

- [x] T020 [P] [US2] Write test
  `test_boox_parse_inline_figure_ref` in
  `tests/test_epub_figures.py` that creates a temp dir
  with an annotation containing "(Figure 1.1)" inline,
  the test EPUB, and verifies the annotation gets a
  FigureRef for "1.1"
- [x] T021 [P] [US2] Write test
  `test_boox_parse_multiple_inline_refs` in
  `tests/test_epub_figures.py` for an annotation with
  two figure references, verifying both are captured

### Implementation for User Story 2

- [x] T022 [US2] Verify `detect_figure_refs` already handles
  inline patterns (implemented in T010). If the Boox parser
  integration from T015 already calls `detect_figure_refs`
  on all annotations (not just captions), this story may
  already work. Run tests to confirm.
- [x] T023 [US2] Run `uv run pytest` — verify inline tests pass

**Checkpoint**: Both caption and inline figure extraction working

---

## Phase 5: User Story 3 — Graceful Fallback Without EPUB (Priority: P2)

**Goal**: Parser works identically to before when no EPUB is
present.

**Independent Test**: Run parser on existing Boox fixture
(no EPUB), verify output unchanged.

### Tests for User Story 3

- [x] T024 [US3] Write test `test_boox_parse_no_epub_unchanged`
  in `tests/test_epub_figures.py` that runs
  `parse_boox_annotations` on the existing
  `tests/fixtures/boox/` fixture (which has no EPUB) and
  verifies all 35 annotations are returned with empty
  `figures` lists and no errors

### Implementation for User Story 3

- [x] T025 [US3] Verify existing Boox parser tests still pass
  (backward compatibility). Run
  `uv run pytest tests/test_boox_parser.py` — all 9 tests
  must pass unchanged

**Checkpoint**: Full backward compatibility confirmed

---

## Phase 6: MCP Integration

**Purpose**: Expose figure data through the MCP tool

- [x] T026 [P] Modify `parse_boox_export` MCP tool in
  `src/otb/mcp_server.py` to include `figures` field
  in annotation dicts (list of `{label, image_path}` dicts)
- [x] T027 [P] Write test `test_parse_boox_export_figures`
  in `tests/test_mcp_server.py` verifying the MCP tool
  returns figure data when EPUB is present
- [x] T028 Run `uv run pytest` — verify all tests pass
- [x] T029 Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix any issues

**Checkpoint**: MCP tool exposes figure data

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T030 Run `pymarkdownlnt scan -r --respect-gitignore .`
  — fix any markdown lint issues
- [x] T031 Run full quality gate suite:
  `uv run pytest && uv run mypy src/ tests/ && uv run pylint src/ tests/`
- [x] T032 Verify with real sample data:
  `uv run otb boox parse tmp/the-power-of-creative-destruction/ /tmp/epub-fig-test/`
  and check `images/` directory contains extracted figures
- [x] T033 Verify backward compat with no-EPUB export:
  `uv run otb boox parse tests/fixtures/boox/ /tmp/boox-nofig-test/`
  and confirm output has no `images/` directory

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (fixture + model)
- **US1 (Phase 3)**: Depends on Foundational (epub_figures module)
- **US2 (Phase 4)**: Depends on US1 (parser integration exists)
- **US3 (Phase 5)**: Depends on US1 (parser modified)
- **MCP (Phase 6)**: Depends on US1 (figures field populated)
- **Polish (Phase 7)**: Depends on all previous phases

### Within Each Phase

- Tests MUST be written and FAIL before implementation
  (Constitution III)
- Tasks marked [P] can run in parallel

### Parallel Opportunities

- T003-T008: All foundational test-writing tasks in parallel
- T013-T014: US1 test tasks in parallel
- T020-T021: US2 test tasks in parallel
- T026-T027: MCP tasks in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (fixture + FigureRef dataclass)
2. Complete Phase 2: Foundational (epub_figures module)
3. Complete Phase 3: US1 (caption figure extraction)
4. **STOP and VALIDATE**: Verify with real sample data
5. Caption-based figure extraction is usable at this point

### Incremental Delivery

1. Setup + Foundational → EPUB parsing works
2. US1 → Caption figures extracted and linked (MVP)
3. US2 → Inline references also handled
4. US3 → Backward compat confirmed
5. MCP → Figures exposed to AI agents
6. Polish → All quality gates green

---

## Notes

- `beautifulsoup4` is already a project dependency — no new
  deps needed (research decision R4)
- EPUB XHTML parsing handles both Pattern A (anchor inside
  figure) and Pattern B (anchor before figure) from research
- `detect_figure_refs` covers both caption and inline patterns
  in one function — US2 may be essentially free after US1
- The `figures` field on Annotation defaults to `[]`, so all
  existing parsers and tests remain compatible

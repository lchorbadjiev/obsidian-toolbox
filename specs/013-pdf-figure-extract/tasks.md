# Tasks: Extract PDF Figures for Zotero Annotations

**Input**: Design documents from `/specs/013-pdf-figure-extract/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md,
contracts/

**Organization**: Tasks grouped by user story for independent
implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to

## Phase 1: Setup

**Purpose**: Add dependency and create test fixtures

- [ ] T001 Add `pypdf` dependency to `pyproject.toml` and run
  `uv sync` to install it
- [ ] T002 Create a minimal test PDF fixture at
  `tests/fixtures/zotero/test.pdf` containing one page with
  an embedded JPEG image and the text "Figure 1-1" on it
  (use pypdf or reportlab to generate programmatically)

**Checkpoint**: Dependency installed, test fixture ready

---

## Phase 2: Foundational — PDF Figure Extraction Module

**Purpose**: Core PDF image extraction that all user stories
depend on

### Tests for Foundational Phase

> **NOTE: Write these tests FIRST, ensure they FAIL before
> implementation (Constitution III)**

- [ ] T003 [P] Write test `test_extract_page_image` in
  `tests/test_pdf_figures.py` verifying that
  `extract_page_image(pdf_path, page_num)` returns
  `(image_bytes, extension)` tuple for the test PDF fixture
- [ ] T004 [P] Write test `test_extract_page_image_no_images`
  in `tests/test_pdf_figures.py` verifying that a page with
  no images returns `None`
- [ ] T005 [P] Write test `test_extract_page_image_missing_pdf`
  in `tests/test_pdf_figures.py` verifying that a nonexistent
  PDF returns `None` (graceful failure)
- [ ] T006 [P] Write test `test_detect_zotero_figure_refs`
  in `tests/test_pdf_figures.py` verifying detection of
  caption pattern `"Figure 5-2. Monolithic architectures"`
  returns `[("5-2", "107")]`
- [ ] T007 [P] Write test
  `test_detect_zotero_figure_refs_inline` in
  `tests/test_pdf_figures.py` verifying detection of inline
  pattern `"as illustrated in Figure 2-1"` with page "26"
  returns `[("2-1", "26")]`
- [ ] T008 [P] Write test
  `test_detect_zotero_figure_refs_request` in
  `tests/test_pdf_figures.py` verifying detection of
  `"Get the figure 5-17"` pattern
- [ ] T009 [P] Write test
  `test_detect_zotero_figure_refs_none` in
  `tests/test_pdf_figures.py` verifying that text with no
  figure references returns `[]`

### Implementation for Foundational Phase

- [ ] T010 Create `src/otb/pdf_figures.py` with:
  `extract_page_image(pdf_path: Path, page_num: int)
  -> tuple[bytes, str] | None` that opens PDF with pypdf,
  accesses the page's images via `page.images`, returns the
  largest image's data and file extension. Returns `None` on
  errors or if no images found. Warns to stderr on failures.
- [ ] T011 Add `detect_zotero_figure_refs(text: str,
  page: str) -> list[tuple[str, str]]` to
  `src/otb/pdf_figures.py` using regex to detect:
  caption `^Figure\s+(\d+[-.]?\d+)`, inline
  `Figure\s+(\d+[-.]?\d+)`, and request
  `[Gg]et the figure\s+(\d+[-.]?\d+)`. Returns list of
  (label, page_str) tuples.
- [ ] T012 Add `extract_pdf_figures(pdf_path: Path,
  refs: list[tuple[str, str]]) -> FigureMap` to
  `src/otb/pdf_figures.py` that iterates over figure refs,
  calls `extract_page_image` for each page, returns a
  FigureMap (label → (bytes, ext)).
- [ ] T013 Run `uv run pytest tests/test_pdf_figures.py`
  and verify all tests pass (green)
- [ ] T014 Run `uv run mypy src/otb/pdf_figures.py` and
  `uv run pylint src/otb/pdf_figures.py` — fix any issues

**Checkpoint**: PDF extraction module working independently

---

## Phase 3: User Story 1 — Caption Figure Extraction (Priority: P1)

**Goal**: Annotations starting with "Figure X-Y." get the
corresponding image extracted from the PDF and linked.

**Independent Test**: Parse Zotero fixture with test PDF,
verify caption annotations get FigureRef objects and images.

### Tests for User Story 1

- [ ] T015 [P] [US1] Write test
  `test_zotero_parse_with_pdf_caption` in
  `tests/test_pdf_figures.py` that creates a temp dir with
  `book.txt`, `Annotations.md` containing a "Figure 1-1."
  caption annotation with page reference, and the test PDF,
  then calls `parse_zotero_annotations` and verifies the
  annotation has a `figures` list with one FigureRef
- [ ] T016 [P] [US1] Write test
  `test_zotero_cli_with_pdf_writes_images` in
  `tests/test_pdf_figures.py` that runs `otb zotero parse`
  on a temp dir with PDF and verifies `images/` directory
  contains extracted figure files and annotations contain
  image links

### Implementation for User Story 1

- [ ] T017 [US1] Modify `parse_zotero_annotations` in
  `src/otb/zotero_parser.py` to: detect `.pdf` file in
  directory, call `detect_zotero_figure_refs` on each
  annotation's text (passing the page string), call
  `extract_pdf_figures` with collected refs, attach
  `FigureRef` objects to annotations. Return
  `(annotations, figure_map)` tuple (same pattern as
  boox_parser).
- [ ] T018 [US1] Update `zotero_parse` CLI command in
  `src/otb/cli.py` to handle the new tuple return from
  `parse_zotero_annotations` and pass figure_data to
  `write_annotations`
- [ ] T019 [US1] Update `parse_zotero_export` MCP tool in
  `src/otb/mcp_server.py` to write figures to a temp dir
  and return `figures_dir` in the summary (same pattern
  as `parse_boox_export`)
- [ ] T020 [US1] Run `uv run pytest` and verify all tests
  pass
- [ ] T021 [US1] Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix any issues

**Checkpoint**: Caption-based PDF figure extraction working
end-to-end

---

## Phase 4: User Story 2 — Inline Figure References (Priority: P2)

**Goal**: Annotations mentioning "Figure X-Y" inline get the
referenced figure extracted and linked.

### Tests for User Story 2

- [ ] T022 [P] [US2] Write test
  `test_zotero_parse_inline_figure_ref` in
  `tests/test_pdf_figures.py` for an annotation containing
  "illustrated in Figure 1-1" inline, verifying FigureRef
  is attached

### Implementation for User Story 2

- [ ] T023 [US2] Verify `detect_zotero_figure_refs` already
  handles inline patterns (implemented in T011). The
  integration from T017 should already detect inline refs.
  Run tests to confirm.

**Checkpoint**: Inline figure references working

---

## Phase 5: User Story 3 — Backward Compatibility (Priority: P2)

### Tests for User Story 3

- [ ] T024 [US3] Write test
  `test_zotero_parse_no_pdf_unchanged` in
  `tests/test_pdf_figures.py` verifying that
  `parse_zotero_annotations` on the existing
  `tests/fixtures/zotero/` directory (no PDF) returns
  annotations with empty `figures` lists and no errors

### Implementation for User Story 3

- [ ] T025 [US3] Verify existing Zotero parser tests still
  pass unchanged. Run
  `uv run pytest tests/test_zotero_parser.py`

**Checkpoint**: Full backward compatibility confirmed

---

## Phase 6: Polish and Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T026 Run `pymarkdownlnt scan -r --respect-gitignore .`
  — fix any markdown lint issues
- [ ] T027 Run full quality gate suite:
  `uv run pytest && uv run mypy src/ tests/ && uv run pylint src/ tests/`
- [ ] T028 Verify with real sample data:
  `uv run otb zotero parse tmp/building-evolutionary-architectures/ /tmp/pdf-fig-test/`
  and check `images/` directory contains extracted figures
- [ ] T029 Verify backward compat with existing fixture:
  `uv run otb zotero parse tests/fixtures/zotero/ /tmp/zotero-nopdf-test/`

---

## Dependencies and Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Setup (pypdf + fixture)
- **US1 (Phase 3)**: Depends on Foundational (pdf_figures module)
- **US2 (Phase 4)**: Depends on US1 (parser integration)
- **US3 (Phase 5)**: Depends on US1 (parser modified)
- **Polish (Phase 6)**: Depends on all previous phases

### Parallel Opportunities

- T003-T009: All foundational tests in parallel
- T015-T016: US1 tests in parallel
- T022: US2 test independent

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (pypdf + fixture)
2. Complete Phase 2: Foundational (pdf_figures module)
3. Complete Phase 3: US1 (caption figure extraction)
4. **STOP and VALIDATE**: Verify with real sample data

### Incremental Delivery

1. Setup + Foundational → PDF extraction works
2. US1 → Caption figures extracted and linked (MVP)
3. US2 → Inline references also handled
4. US3 → Backward compat confirmed
5. Polish → All quality gates green

---

## Notes

- `pypdf` is pure Python — no binary deps (research R1)
- PDF figures are extracted as JPEG bytes directly from page
  resources — no rendering needed
- When a page has multiple images, the largest by byte size
  is selected as the figure (research R4)
- Reuses `FigureRef` dataclass and `md_writer` figure support
  from the EPUB figure feature
- `detect_zotero_figure_refs` handles both "Figure X-Y"
  (hyphen) and "Figure X.Y" (dot) patterns
- Also detects explicit "Get the figure X-Y" user requests

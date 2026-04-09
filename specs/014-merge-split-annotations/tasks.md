# Tasks: Merge Split Zotero Annotations

**Input**: Design documents from
`/specs/014-merge-split-annotations/`
**Prerequisites**: plan.md, spec.md, research.md

**Organization**: Small feature — merge logic + integration.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to

## Phase 1: User Story 1 — Merge Adjacent-Page Pairs (Priority: P1)

**Goal**: Detect and merge consecutive Zotero annotations on
adjacent pages when PDF text confirms they are adjacent.

### Tests for User Story 1

> Write tests FIRST (Constitution III)

- [x] T001 [P] [US1] Write test
  `test_merge_split_annotations_basic` in
  `tests/test_pdf_figures.py` that creates two annotations
  on pages 1 and 2 whose texts are adjacent in a test PDF,
  calls `merge_split_annotations`, and verifies they merge
  into one annotation with concatenated text
- [x] T002 [P] [US1] Write test
  `test_merge_split_annotations_not_adjacent` in
  `tests/test_pdf_figures.py` that creates two annotations
  on adjacent pages whose texts are far apart in the PDF,
  and verifies they remain separate
- [x] T003 [P] [US1] Write test
  `test_merge_split_annotations_no_pdf` in
  `tests/test_pdf_figures.py` that calls merge with
  `pdf_path=None` and verifies annotations are returned
  unchanged
- [x] T004 [P] [US1] Write test
  `test_merge_regenerates_title` in
  `tests/test_pdf_figures.py` verifying the merged
  annotation's title is regenerated from the combined text

### Implementation for User Story 1

- [x] T005 [US1] Add `extract_page_text(pdf_path: Path,
  page_num: int) -> str` to `src/otb/pdf_figures.py` that
  reads a PDF page's text content using pypdf. Returns empty
  string on failure.
- [x] T006 [US1] Add `merge_split_annotations(annotations:
  list[Annotation], pdf_path: Path | None) ->
  list[Annotation]` to `src/otb/pdf_figures.py`. For each
  consecutive pair on adjacent pages (page N, N+1): extract
  text from pages N and N+1, search for tail of annotation A
  (last 30 chars) and head of annotation B (first 30 chars)
  in combined text, merge if gap <= 200 chars. Support
  chained merges. Regenerate title via `_title_from_text`.
- [x] T007 [US1] Call `merge_split_annotations` in
  `parse_zotero_annotations` in `src/otb/zotero_parser.py`
  after initial parsing but before figure extraction and
  numbering. Pass the PDF path (or None if no PDF).
- [x] T008 [US1] Run `uv run pytest tests/test_pdf_figures.py
  -k merge` and verify all merge tests pass
- [x] T009 [US1] Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix any issues

**Checkpoint**: Merge logic working with tests

---

## Phase 2: Polish and Validation

- [x] T010 Run `uv run pytest` — verify all tests pass
- [x] T011 Run full quality gate suite:
  `uv run mypy src/ tests/ && uv run pylint src/ tests/`
- [x] T012 Verify with real sample:
  `uv run otb zotero parse tmp/building-evolutionary-architectures/ /tmp/merge-test/`
  and confirm "Donella H. Meadows" merged with
  "Multiple Architectural Dimensions" annotation
- [x] T013 Verify backward compat without PDF:
  run on `tests/fixtures/zotero/` (no PDF) and confirm
  306 annotations unchanged

---

## Dependencies and Execution Order

- **US1 (Phase 1)**: No dependencies — start immediately
- **Polish (Phase 2)**: Depends on Phase 1

### Parallel Opportunities

- T001-T004: All test tasks in parallel

---

## Implementation Strategy

### MVP

1. Write tests T001-T004
2. Implement T005-T007 (merge function + integration)
3. Verify T008-T009
4. Polish T010-T013

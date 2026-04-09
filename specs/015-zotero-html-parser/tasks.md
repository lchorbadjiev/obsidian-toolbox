# Tasks: Parse Zotero HTML Exports with Colors

**Input**: Design documents from
`/specs/015-zotero-html-parser/`
**Prerequisites**: plan.md, spec.md, research.md

**Organization**: Tasks grouped by user story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: Which user story this task belongs to

## Phase 1: Setup

**Purpose**: Create HTML fixture

- [x] T001 Copy `Annotations.html` from
  `tmp/building-evolutionary-architectures/` to
  `tests/fixtures/zotero/Annotations.html`

**Checkpoint**: HTML fixture ready

---

## Phase 2: User Story 1 — Parse HTML with Colors (Priority: P1)

**Goal**: Parse Zotero HTML export and extract annotations with
highlight colors preserved.

### Tests for User Story 1

> Write tests FIRST (Constitution III)

- [x] T002 [P] [US1] Write test `test_parse_html_annotation_count`
  in `tests/test_zotero_parser.py` verifying that parsing the
  HTML fixture returns the same number of annotations as the
  markdown fixture (205 after merge)
- [x] T003 [P] [US1] Write test `test_parse_html_first_annotation`
  in `tests/test_zotero_parser.py` verifying the first
  annotation has correct text, page ("14"), and color
  ("#ffd400")
- [x] T004 [P] [US1] Write test `test_parse_html_color_variety`
  in `tests/test_zotero_parser.py` verifying at least 3
  distinct color values are present across all annotations
- [x] T005 [P] [US1] Write test
  `test_parse_html_color_stripped_alpha` in
  `tests/test_zotero_parser.py` verifying colors are 7-char
  hex strings (e.g., "#ffd400") not 9-char with alpha

### Implementation for User Story 1

- [x] T006 [US1] Add `_parse_html_annotations` function to
  `src/otb/zotero_parser.py` that reads an HTML file with
  BeautifulSoup, finds all `<p>` elements containing
  `<span class="highlight">`, extracts text from the inner
  colored `<span>`, extracts page from
  `<span class="citation-item">` (regex `p\.\s*(\w+)`),
  extracts color from `background-color` style (strip last
  2 hex digits for alpha), returns list of
  `(text, page, color)` tuples
- [x] T007 [US1] Modify `parse_zotero_annotations` in
  `src/otb/zotero_parser.py` to check for
  `Annotations.html` first. If found, call
  `_parse_html_annotations` instead of the markdown regex
  parser. Pass colors through to Annotation objects.
  If only `Annotations.md` exists, use existing parser.
- [x] T008 [US1] Run `uv run pytest tests/test_zotero_parser.py
  -k html` and verify all HTML tests pass
- [x] T009 [US1] Run `uv run mypy src/otb/zotero_parser.py`
  and `uv run pylint src/otb/zotero_parser.py` — fix issues

**Checkpoint**: HTML parsing with colors working

---

## Phase 3: User Story 2 — Full Pipeline Integration (Priority: P1)

**Goal**: All downstream features work with HTML input.

### Tests for User Story 2

- [x] T010 [P] [US2] Write test
  `test_parse_html_with_word_fixing` in
  `tests/test_zotero_parser.py` verifying that word
  concatenation fixing still works on HTML-parsed annotations
  (check "SoftwareWithout" is not present in output)
- [x] T011 [P] [US2] Write test
  `test_html_color_in_markdown_output` in
  `tests/test_md_writer.py` verifying that an annotation
  with `color="#ffd400"` produces frontmatter containing
  `color: "#ffd400"`

### Implementation for User Story 2

- [x] T012 [US2] Modify `_render` in `src/otb/md_writer.py`
  to include `color: "{color}"` in the frontmatter when
  `a.color` is not None
- [x] T013 [US2] Run `uv run pytest` and verify all tests pass
- [x] T014 [US2] Run `uv run mypy src/ tests/` and
  `uv run pylint src/ tests/` — fix issues

**Checkpoint**: Full pipeline working with HTML + colors

---

## Phase 4: User Story 3 — Backward Compatibility (Priority: P2)

### Tests for User Story 3

- [x] T015 [US3] Write test `test_fallback_to_markdown` in
  `tests/test_zotero_parser.py` that runs parser on a temp
  dir with only `Annotations.md` (no HTML) and verifies
  annotations are parsed with `color=None`
- [x] T016 [US3] Write test `test_prefer_html_over_markdown`
  in `tests/test_zotero_parser.py` that runs parser on the
  fixture dir (which has both files) and verifies colors
  are present (HTML was used)

### Implementation for User Story 3

- [x] T017 [US3] Verify existing markdown-only Zotero tests
  still pass: `uv run pytest tests/test_zotero_parser.py`

**Checkpoint**: Backward compatibility confirmed

---

## Phase 5: Polish and Validation

- [x] T018 Run `uv run pytest` — verify all tests pass
- [x] T019 Run full quality gate suite:
  `uv run mypy src/ tests/ && uv run pylint src/ tests/`
- [x] T020 Verify with real sample:
  `uv run otb zotero parse tmp/building-evolutionary-architectures/ /tmp/html-test/`
  and check colors in frontmatter
- [x] T021 Run `pymarkdownlnt scan -r --respect-gitignore .`
  — fix any markdown lint issues

---

## Dependencies and Execution Order

- **Setup (Phase 1)**: No dependencies
- **US1 (Phase 2)**: Depends on Setup (fixture)
- **US2 (Phase 3)**: Depends on US1 (HTML parser)
- **US3 (Phase 4)**: Depends on US1 (format detection)
- **Polish (Phase 5)**: Depends on all

### Parallel Opportunities

- T002-T005: All US1 tests in parallel
- T010-T011: US2 tests in parallel

---

## Implementation Strategy

### MVP (User Story 1)

1. Setup fixture
2. HTML parser + format detection
3. Verify colors preserved

### Incremental

1. US1 → HTML parsing with colors (MVP)
2. US2 → Full pipeline + color in markdown output
3. US3 → Backward compat confirmed
4. Polish → All gates green

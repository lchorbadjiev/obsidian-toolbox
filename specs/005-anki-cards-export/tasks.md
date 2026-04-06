# Tasks: Export Book Annotations to Anki

**Input**: Design documents from `/specs/005-anki-cards-export/`
**Branch**: `005-anki-cards-export`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (touches different files, no blocking dependency)
- **[Story]**: Which user story this task belongs to (US1 / US2 / US3)
- Exact file paths included in every description

---

## Phase 1: Setup

**Purpose**: Confirm clean baseline before any changes.

- [x] T001 Run `uv run pytest` on `005-anki-cards-export` branch and confirm
  all existing tests pass (zero failures required before any new code is
  written)

---

## Phase 2: Foundational — Extend Annotation Data Model

**Purpose**: Add `anki_id` support to the shared `Annotation` dataclass and
the markdown parser/writer. Every user story depends on these changes.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T002 [P] Write failing test: `Annotation` dataclass accepts
  `anki_id: int | None = None` and defaults to `None` in
  `tests/test_parser.py`
- [x] T003 [P] Write failing test: `parse_annotation_md` reads `anki_id`
  from frontmatter when present and returns `None` when absent, in
  `tests/test_md_parser.py` (add a fixture file with `anki_id:
  1234567890` to `tests/fixtures/annotations/`)
- [x] T004 [P] Write failing test: `write_anki_id(path, anki_id)` inserts
  `anki_id: <value>` into an existing annotation markdown file's
  frontmatter in `tests/test_md_writer.py`
- [x] T005 Add `anki_id: int | None = None` field to the `Annotation`
  dataclass in `src/otb/parser.py` (after `number`; default `None` so all
  existing call sites remain valid)
- [x] T006 Update `_parse_frontmatter` result usage in `src/otb/md_parser.py`
  to read `anki_id` and set `Annotation.anki_id = int(fm["anki_id"])` when
  the key is present; leave `None` when absent. Also add
  `parse_annotation_dir_with_paths(directory: Path) -> list[tuple[Path,
  Annotation]]` returning `(file_path, annotation)` pairs sorted by
  filename.
- [x] T007 Add `write_anki_id(path: Path, anki_id: int) -> None` to
  `src/otb/md_writer.py`. The function reads the file, inserts or replaces
  the `anki_id: <value>` line in the frontmatter block (between `---`
  delimiters), and writes the file back atomically. Raises `OSError` on
  write failure (caller handles the warning).

**Checkpoint**: `uv run pytest` green; `Annotation.anki_id` round-trips
through parse and write; `parse_annotation_dir_with_paths` returns file paths.

---

## Phase 3: User Story 1 — Export Annotations to Anki Deck (Priority: P1) 🎯 MVP

**Goal**: Run `otb anki export <dir>` to create Anki cards from all
annotations in a directory and write `anki_id` back to each markdown file.

**Independent Test**: Point the command at the fixture annotations directory
(with AnkiConnect running). Verify cards appear in Anki, card count matches
annotation count, and each `.md` file's frontmatter has `anki_id` set.

### Tests for User Story 1

> **Write these tests FIRST — confirm they FAIL before any implementation**

- [x] T008 [P] [US1] Write failing tests for `build_card(annotation,
  deck_name) -> dict` covering: chapter present, chapter empty, title
  empty (falls back to text snippet) in `tests/test_anki.py`
- [x] T009 [P] [US1] Write failing tests for `AnkiClient._call` using
  `unittest.mock.patch("urllib.request.urlopen")`: success response,
  non-null `error` field raises `AnkiConnectError`, connection refused
  raises `AnkiConnectError` in `tests/test_anki.py`
- [x] T010 [P] [US1] Write failing tests for `export_annotations`: all
  annotations new (all created + IDs written back), annotation with
  `anki_id` already set (skipped), blank text annotation (skipped),
  `write_anki_id` raises `OSError` (card counted as created + warning
  emitted) in `tests/test_anki.py`
- [x] T011 [P] [US1] Write failing CLI tests for `otb anki export <dir>`:
  happy path prints `Created: N  Skipped: 0  Failed: 0`, non-directory
  path rejected with error, Anki unreachable exits non-zero with stderr
  message in `tests/test_cli.py`

### Implementation for User Story 1

- [x] T012 [US1] Create `src/otb/anki.py` with `AnkiConnectError(Exception)`
  and `AnkiClient(url: str)` containing `_call(action, **params) -> Any`,
  `create_deck(deck: str) -> None`, and `add_notes(notes: list[dict]) ->
  list[int | None]`. Use `urllib.request.urlopen` with JSON body
  `{"action": ..., "version": 6, "params": {...}}`. Raise
  `AnkiConnectError` on `urllib.error.URLError` or non-null top-level
  `error` field.
- [x] T013 [US1] Add `build_card(annotation: Annotation, deck_name: str) ->
  dict` and `ExportResult(created, skipped, failed)` frozen dataclass to
  `src/otb/anki.py`. `build_card` sets `Front` to `"{chapter} —
  {title}"` when chapter is non-empty, else `"{title}"`; if title is also
  empty uses first 60 chars of text (ellipsised). `Back` is always the
  full annotation text. `modelName` is `"Basic"`, `options.allowDuplicate`
  is `false`.
- [x] T014 [US1] Implement `export_annotations(annotated_paths:
  list[tuple[Path, Annotation]], deck: str, anki_url: str) -> ExportResult`
  in `src/otb/anki.py`. Flow: (1) skip annotations with blank text and
  those with `anki_id` already set; (2) call `create_deck`; (3) batch
  `add_notes` for remaining annotations; (4) for each returned non-null
  ID call `write_anki_id(path, id)` — catch `OSError`, emit
  `click.echo(..., err=True)` warning, still count as created; (5) return
  `ExportResult`.
- [x] T015 [US1] Add `anki` Click group and `export` subcommand to
  `src/otb/cli.py`. Accept `PATH` as `click.Path(exists=True,
  file_okay=False, path_type=Path)`. Options: `--deck` (default `""`),
  `--anki-url` (default `"http://localhost:8765"`). Call
  `parse_annotation_dir_with_paths(path)`, derive deck name from first
  annotation's book title when `--deck` is empty, call
  `export_annotations`, print summary to stdout. Catch
  `AnkiConnectError` → print to stderr, `sys.exit(1)`.

**Checkpoint**: `otb anki export tests/fixtures/annotations/` works end-to-end
(with Anki running). Summary line printed. Each fixture `.md` file has
`anki_id` set after the run. All US1 tests pass.

---

## Phase 4: User Story 2 — Specify Target Deck Name (Priority: P2)

**Goal**: `--deck "Parent::Child"` routes cards to the named deck, creating it
if it does not exist, including nested deck hierarchy.

**Independent Test**: Run `otb anki export <dir> --deck "Test::Books"`. Verify
the deck `Test::Books` is created in Anki and all cards land there.

### Tests for User Story 2

> **Write these tests FIRST — confirm they FAIL before any implementation**

- [x] T016 [P] [US2] Write failing CLI test: `otb anki export <dir> --deck
  "Non-Fiction::History"` passes `"Non-Fiction::History"` as the deck
  name to `export_annotations` (mock `export_annotations` and assert
  call args) in `tests/test_cli.py`
- [x] T017 [P] [US2] Write failing unit test: `AnkiClient.create_deck` is
  called with the exact string `"Non-Fiction::History"` when `--deck` is
  set (AnkiConnect creates nested decks from the full path string) in
  `tests/test_anki.py`

### Implementation for User Story 2

- [x] T018 [US2] Verify `export_annotations` uses the `deck` argument as-is
  in `AnkiClient.create_deck` and in each note's `deckName` field. If the
  deck name contains `::` AnkiConnect automatically creates parent decks —
  no extra handling needed. Fix any gaps found in `src/otb/anki.py` and
  `src/otb/cli.py`.

**Checkpoint**: `--deck "Parent::Child"` creates the nested deck. US2 tests
pass alongside all US1 tests.

---

## Phase 5: User Story 3 — Skip Already-Exported Annotations (Priority: P3)

**Goal**: On a second run, annotations with `anki_id` set are checked against
Anki. Those whose note still exists are skipped; those whose note was deleted
are re-created and `anki_id` is overwritten.

**Independent Test**: Export a directory, then delete one card from Anki
manually, then re-run. Verify: previously-exported annotations are skipped,
the deleted card is recreated, `anki_id` for the recreated annotation is
updated in its markdown file.

### Tests for User Story 3

> **Write these tests FIRST — confirm they FAIL before any implementation**

- [x] T019 [P] [US3] Write failing test for `AnkiClient.notes_info([id1,
  id2])` using mocked `urlopen`: returns list of note dicts for found IDs
  and `None` for missing IDs in `tests/test_anki.py`
- [x] T020 [P] [US3] Write failing test for `export_annotations` stale-ID
  path: annotation has `anki_id=999` but `notes_info` returns `None` for
  that ID → card is re-created, `write_anki_id` called with new ID in
  `tests/test_anki.py`
- [x] T021 [P] [US3] Write failing test for `export_annotations` valid-ID
  path: annotation has `anki_id=888` and `notes_info` returns a note dict
  → annotation is skipped, `add_notes` not called for it in
  `tests/test_anki.py`

### Implementation for User Story 3

- [x] T022 [US3] Add `notes_info(note_ids: list[int]) -> list[dict[str,
  Any] | None]` to `AnkiClient` in `src/otb/anki.py`. Calls AnkiConnect
  action `"notesInfo"` with `{"notes": note_ids}`. Returns the result
  array (element is `None` when the note does not exist in Anki).
- [x] T023 [US3] Update `export_annotations` in `src/otb/anki.py` to
  replace the simple `anki_id is not None → skip` logic with a
  verification step: collect all non-null `anki_id` values, batch-call
  `notes_info`, partition into confirmed-existing (skip) and stale
  (treat as new — clear `anki_id` before building card). Re-create stale
  cards and write back new IDs.

**Checkpoint**: Second run skips existing cards, re-creates deleted ones, and
updates `anki_id`. All US1 + US2 + US3 tests pass.

---

## Phase 6: MCP Tool (Constitution Principle VI)

**Goal**: Expose `anki_export` as an MCP tool so AI agents can call it
directly. Delegates to `export_annotations` with no logic duplication.

**Independent Test**: Run `uv run pytest tests/test_mcp_server.py` and confirm
the new tool's input schema, output schema, and error responses are correct.

### Tests for Phase 6

> **Write these tests FIRST — confirm they FAIL before any implementation**

- [x] T024 [P] Write failing MCP tool tests: `anki_export(path, deck="",
  anki_url="http://localhost:8765")` returns `{"created": N, "skipped":
  M, "failed": 0}`; `FileNotFoundError` on bad path; `AnkiConnectError`
  produces MCP error response in `tests/test_mcp_server.py`

### Implementation for Phase 6

- [x] T025 Add `anki_export(path: str, deck: str = "", anki_url: str =
  "http://localhost:8765") -> dict[str, Any]` MCP tool to
  `src/otb/mcp_server.py`. Resolve `path` to `Path`, raise
  `FileNotFoundError` if absent, call
  `parse_annotation_dir_with_paths`, derive deck name from first
  annotation when `deck=""`, call `export_annotations`, return
  `{"created": ..., "skipped": ..., "failed": ...}`.

**Checkpoint**: `uv run pytest tests/test_mcp_server.py` passes including new
tool tests.

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T026 Update `specs/005-anki-cards-export/plan.md` to remove all
  references to Kindle HTML file input and replace with markdown-directory-
  only scope (reflects clarification from `/speckit.clarify` session)
- [x] T027 [P] Run `uv run mypy src/ tests/` and fix all type errors to
  achieve zero-error target (pay attention to `int | None` annotations and
  `list[tuple[Path, Annotation]]` return types)
- [x] T028 [P] Run `uv run pylint src/ tests/` and fix to 10/10 (add
  justified suppression comments where rules genuinely cannot be
  satisfied; check `too-many-instance-attributes` on `Annotation` if
  needed)
- [x] T029 Run `uv run pytest` and confirm all tests pass with zero failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks all user stories**
- **US1 (Phase 3)**: Depends on Phase 2 — core deliverable, MVP
- **US2 (Phase 4)**: Depends on Phase 3 (reuses `export_annotations` wiring)
- **US3 (Phase 5)**: Depends on Phase 3 (extends `export_annotations`)
- **MCP (Phase 6)**: Depends on Phase 3 (delegates to `export_annotations`)
- **Polish (Phase 7)**: Depends on all phases complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2/US3
- **US2 (P2)**: Can start after US1 (verifies wiring already done in US1)
- **US3 (P3)**: Can start after US1 (extends the service function from US1)
- **MCP**: Can start after US1 (delegates without modification)
- US2, US3, and MCP can proceed in parallel once US1 is complete

### Within Each Phase

- Test tasks (T-numbers with "failing test" description) MUST be written
  and confirmed to fail before the corresponding implementation task
- Tests marked `[P]` within a phase can be written in parallel
- Implementation tasks proceed after their test tasks fail as expected

---

## Parallel Example: Phase 2 (Foundational)

```
# Write all three failing test tasks together:
Task T002: "Write failing test for Annotation.anki_id in tests/test_parser.py"
Task T003: "Write failing test for anki_id round-trip in tests/test_md_parser.py"
Task T004: "Write failing test for write_anki_id in tests/test_md_writer.py"

# Then implement together:
Task T005: "Add anki_id field to Annotation in src/otb/parser.py"
Task T006: "Update md_parser.py + add parse_annotation_dir_with_paths"
Task T007: "Add write_anki_id to src/otb/md_writer.py"
```

## Parallel Example: Phase 3 (US1 Tests)

```
# All four test tasks can be written in parallel:
Task T008: "build_card tests in tests/test_anki.py"
Task T009: "AnkiClient._call tests in tests/test_anki.py"
Task T010: "export_annotations tests in tests/test_anki.py"
Task T011: "CLI tests for otb anki export in tests/test_cli.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline check)
2. Complete Phase 2: Foundational (data model — blocks everything)
3. Complete Phase 3: User Story 1 (core export + write-back)
4. **STOP and VALIDATE**: `otb anki export <dir>` works end-to-end
5. Deliver MVP

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. Phase 3 (US1) → MVP: export works, `anki_id` persisted
3. Phase 4 (US2) → `--deck` override confirmed
4. Phase 5 (US3) → Stale card re-creation confirmed
5. Phase 6 (MCP) → AI agent access enabled
6. Phase 7 (Polish) → Lint/types clean, plan.md updated

### Parallel Opportunities After US1

Once Phase 3 (US1) is complete, these can proceed in parallel:

- Developer A: Phase 5 (US3 — extends `export_annotations`)
- Developer B: Phase 6 (MCP tool — wraps `export_annotations`)

Phase 4 (US2) is so small it can be done alongside either.

---

## Notes

- Constitution Principle III (Test-First) is NON-NEGOTIABLE: every task
  with a paired test task requires the test to fail before implementation
  begins
- `[P]` tasks touch different files and have no incomplete dependencies
- The `Annotation.anki_id` field must default to `None` to keep all
  existing call sites valid without modification
- `write_anki_id` must handle the case where `anki_id` is already in the
  frontmatter (update, not duplicate)
- The `export_annotations` function takes `list[tuple[Path, Annotation]]`
  so it can write back IDs without needing to reconstruct file paths
- Commit after each checkpoint to keep the branch history clean

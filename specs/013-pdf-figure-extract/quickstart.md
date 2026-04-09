# Quickstart: PDF Figure Extraction

**Feature**: 013-pdf-figure-extract
**Date**: 2026-04-09

## Prerequisites

- Python 3.12+
- `uv sync` (install dependencies including new pypdfium2)

## Setup

Add new dependency:

```bash
uv add pypdfium2 Pillow
uv sync
```

## Development Workflow

### 1. Create test PDF fixture

Create a minimal PDF with one "Figure 1-1" label at
`tests/fixtures/zotero/test.pdf`.

### 2. Write failing tests first (Constitution III)

```bash
uv run pytest tests/test_pdf_figures.py  # should FAIL
```

### 3. Implement pdf_figures module

Create `src/otb/pdf_figures.py` with rendering functions.

```bash
uv run pytest tests/test_pdf_figures.py  # should PASS
```

### 4. Integrate with zotero_parser

Modify `parse_zotero_annotations` for figure detection.

### 5. Quality gates

```bash
uv run pytest
uv run mypy src/ tests/
uv run pylint src/ tests/
```

## Verification with Sample Data

```bash
uv run otb zotero parse \
  tmp/building-evolutionary-architectures/ \
  /tmp/pdf-fig-test/

ls /tmp/pdf-fig-test/images/
# Should contain figure-2-1.png, figure-5-2.png, etc.
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/pdf_figures.py` | PDF page rendering |
| `src/otb/zotero_parser.py` | Modified for figure detection |
| `tests/test_pdf_figures.py` | PDF figure tests |
| `tests/fixtures/zotero/test.pdf` | Minimal test PDF |

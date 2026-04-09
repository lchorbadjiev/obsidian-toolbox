# Quickstart: Extract EPUB Figures for Annotations

**Feature**: 011-epub-figure-extract
**Date**: 2026-04-09

## Prerequisites

- Python 3.12+
- `uv sync` (install dependencies)
- Sample Boox exports in `tmp/` directories

## Development Workflow

### 1. Create minimal test EPUB fixture

Build a small test EPUB with 1-2 figures for
`tests/fixtures/boox/test.epub`. The fixture should contain
at least one XHTML file with a `<figure>` element and one
image file.

### 2. Write failing tests first (Constitution III)

```bash
uv run pytest tests/test_epub_figures.py  # should FAIL (red)
```

### 3. Implement epub_figures module

Create `src/otb/epub_figures.py` with:

- `parse_epub_figures(epub_path) -> EpubFigureMap`
- `detect_figure_refs(text) -> list[str]`

```bash
uv run pytest tests/test_epub_figures.py  # should PASS (green)
```

### 4. Integrate with boox_parser

Modify `parse_boox_annotations` to accept optional EPUB path,
detect figure references, and attach FigureRef objects to
annotations.

### 5. Extend md_writer

Modify `write_annotation` to write images and embed links
when figures are present.

### 6. Quality gates

```bash
uv run pytest                                 # all tests pass
uv run mypy src/ tests/                       # zero errors
uv run pylint src/ tests/                     # 10/10
pymarkdownlnt scan -r --respect-gitignore .   # zero errors
```

## Verification with Sample Data

```bash
uv run otb boox parse \
  tmp/the-power-of-creative-destruction/ \
  /tmp/epub-fig-test/

ls /tmp/epub-fig-test/images/
# Should contain figure-2-1.jpg, figure-2-3.jpg, etc.
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/epub_figures.py` | EPUB figure extraction |
| `src/otb/boox_parser.py` | Modified for figure detection |
| `src/otb/md_writer.py` | Modified for image links |
| `tests/test_epub_figures.py` | Figure extraction tests |
| `tests/fixtures/boox/test.epub` | Minimal test EPUB |

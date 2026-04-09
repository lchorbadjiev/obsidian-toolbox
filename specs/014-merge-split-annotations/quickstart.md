# Quickstart: Merge Split Annotations

**Feature**: 014-merge-split-annotations
**Date**: 2026-04-09

## Development Workflow

### 1. Write failing tests

```bash
uv run pytest tests/test_pdf_figures.py -k merge  # FAIL
```

### 2. Implement merge logic

Add `merge_split_annotations` to `src/otb/pdf_figures.py`
and call it from `src/otb/zotero_parser.py`.

```bash
uv run pytest tests/test_pdf_figures.py -k merge  # PASS
```

### 3. Quality gates

```bash
uv run pytest && uv run mypy src/ tests/ && \
  uv run pylint src/ tests/
```

## Verification

```bash
uv run otb zotero parse \
  tmp/building-evolutionary-architectures/ \
  /tmp/merge-test/

# Check that "Donella H. Meadows" is part of annotation
# starting with "Multiple Architectural Dimensions"
grep -l "Meadows" /tmp/merge-test/*.md
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/pdf_figures.py` | Add merge function |
| `src/otb/zotero_parser.py` | Call merge pass |
| `tests/test_pdf_figures.py` | Add merge tests |

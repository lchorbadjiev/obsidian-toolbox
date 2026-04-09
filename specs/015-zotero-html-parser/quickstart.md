# Quickstart: Zotero HTML Parser

**Feature**: 015-zotero-html-parser
**Date**: 2026-04-09

## Development Workflow

### 1. Create HTML fixture

Copy sample HTML to test fixtures:

```bash
cp tmp/building-evolutionary-architectures/Annotations.html \
   tests/fixtures/zotero/
```

### 2. Write failing tests

```bash
uv run pytest tests/test_zotero_parser.py -k html  # FAIL
```

### 3. Implement HTML parser

Add `_parse_html_annotations` to `src/otb/zotero_parser.py`
and format detection in `parse_zotero_annotations`.

```bash
uv run pytest tests/test_zotero_parser.py -k html  # PASS
```

### 4. Add color to markdown output

Modify `_render` in `src/otb/md_writer.py` to include
`color:` in frontmatter.

### 5. Quality gates

```bash
uv run pytest && uv run mypy src/ tests/ && \
  uv run pylint src/ tests/
```

## Verification

```bash
uv run otb zotero parse \
  tmp/building-evolutionary-architectures/ \
  /tmp/html-color-test/

# Check colors are preserved
head -10 /tmp/html-color-test/001*.md
# Should show color: #ffd400 in frontmatter
```

## Key Files

| File | Purpose |
|------|---------|
| `src/otb/zotero_parser.py` | HTML parser + detection |
| `src/otb/md_writer.py` | Color in frontmatter |
| `tests/test_zotero_parser.py` | HTML parsing tests |
| `tests/fixtures/zotero/Annotations.html` | HTML fixture |

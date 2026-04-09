# Research: Parse Zotero HTML Exports with Colors

**Feature**: 015-zotero-html-parser
**Date**: 2026-04-09

## R1: Zotero HTML Export Structure

**Decision**: Parse using BeautifulSoup with the existing
`html.parser` backend.

**Rationale**: The HTML structure is simple and consistent.
Each annotation is a `<p>` element containing:

```html
<p>
  <span class="highlight">
    <span style="background-color: #ffd40080">
      "annotation text here"
    </span>
  </span>
  <span class="citation">
    (<span class="citation-item">
      "Book Title", p. 42
    </span>)
  </span>
</p>
```

BeautifulSoup is already used by the Kindle parser and the
EPUB figure extractor. No new dependency needed.

### Color Extraction

Colors are 8-digit hex with alpha channel (e.g., `#ffd40080`).
Strip the last 2 characters to get the 6-digit color:
`#ffd40080` → `#ffd400`.

### Observed Colors in Sample

| Hex (with alpha) | Hex (stripped) | Color  |
|------------------|----------------|--------|
| `#ffd40080`      | `#ffd400`      | Yellow |
| `#2ea8e580`      | `#2ea8e5`      | Blue   |
| `#f1983780`      | `#f19837`      | Orange |
| `#ff666680`      | `#ff6666`      | Red    |

## R2: Format Auto-Detection

**Decision**: Check for `Annotations.html` first; fall back to
`Annotations.md` if not found.

**Rationale**: HTML is strictly richer (contains colors). When
both exist, HTML is preferred. This is a simple file-existence
check at the start of `parse_zotero_annotations`.

## R3: Color in Markdown Output

**Decision**: Add `color: #ffd400` to the frontmatter of
annotation markdown files when color is present.

**Rationale**: The `md_writer._render` function already outputs
frontmatter fields. Adding color is a one-line change. The
`color` field on `Annotation` already exists (`str | None`)
and is already serialized in `_annotation_to_dict` for MCP.

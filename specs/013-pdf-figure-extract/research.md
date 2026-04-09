# Research: Extract PDF Figures for Zotero Annotations

**Feature**: 013-pdf-figure-extract
**Date**: 2026-04-09

## R1: PDF Image Extraction Library

**Decision**: Use `pypdf` for direct image extraction from PDF
pages. No page rendering needed.

**Rationale**: Testing on the sample PDF showed that pypdf can
extract actual figure images directly as JPEG bytes from PDF
page resources. This is far superior to full-page screenshots:

- Images are already JPEG-compressed, ready to save as-is
- Individual figures extracted (not full pages)
- Pure Python — no binary dependencies or system tools
- Sample results: Figure 2-1 → 1230x537px JPEG (101KB),
  Figure 5-2 → 1073x1377px JPEG (187KB)

**Alternatives considered**:

- `pypdfium2`: Renders entire pages as bitmaps. Heavier
  (bundles PDFium binary). Overkill when images can be
  extracted directly.
- `pymupdf` (fitz): C++ bindings. Heavier than needed.
- `pdf2image`: Requires system `poppler`. Not portable.
- Full-page screenshots: Lower quality, larger files, include
  text around the figure.

### API Usage

```python
from pypdf import PdfReader

def extract_images_from_page(pdf_path, page_num):
    reader = PdfReader(pdf_path)
    page = reader.pages[page_num]
    images = []
    for image_obj in page.images:
        images.append((image_obj.name, image_obj.data))
    return images
```

### Key Finding

PDF figures use DCTDecode (JPEG) compression. The raw bytes
from `image_obj.data` are valid JPEG files that can be saved
directly — no Pillow or re-encoding needed.

## R2: Figure Reference Detection in Zotero Annotations

**Decision**: Reuse the `detect_figure_refs` function from
`epub_figures.py` with an extended regex to handle Zotero's
hyphenated figure numbers (e.g., "Figure 2-1" alongside
"Figure 2.1").

**Rationale**: Zotero annotations from O'Reilly books use
"Figure X-Y" (hyphen) while the EPUB feature detects
"Figure X.Y" (dot). A single regex can handle both:
`Figure\s+(\d+[-.]?\d+[a-z]?)`.

Additionally, detect explicit user requests like "Get the
figure X-Y" which appear as standalone annotations in the
sample data.

**Patterns observed in sample data**:

- Caption: `"Figure 5-2. Monolithic architectures..."`
- Inline: `"...as illustrated in Figure 2-1"`
- User request: `"Get the figure 5-2"`

## R3: Page Number Mapping

**Decision**: Use the page string from the Zotero annotation
(e.g., "26") directly as the PDF page index. Zotero stores
physical page numbers that map 1:1 to PDF pages (0-indexed
in pypdfium2, so subtract 1).

**Rationale**: The sample data shows annotations with page
numbers like `p. 26`, `p. 107`. These correspond to the
physical PDF pages. For figure captions, the figure is on
the same page as the annotation. For inline references, the
figure may be on a nearby page — start with the annotation's
page.

## R4: Image Identification Strategy

**Decision**: Extract images from the page referenced by the
annotation. When a page has exactly one image, it is the
figure. When a page has multiple images, use positional
heuristics or extract all and let the user pick.

**Rationale**: The sample PDF typically has one figure image
per page. For pages with multiple images (e.g., decorative
elements plus a chart), extracting all is safe — the figure
image is usually the largest one.

**Approach**:
1. Look up the annotation's page number
2. Extract all images from that PDF page
3. If one image: use it directly
4. If multiple images: use the largest by byte size
5. If no images on that page: warn and skip

# Research: Extract EPUB Figures for Annotations

**Feature**: 011-epub-figure-extract
**Date**: 2026-04-09

## R1: EPUB Figure-to-Image Mapping Strategy

**Decision**: Parse EPUB XHTML content with BeautifulSoup to
build a mapping from figure labels (e.g., "2.1") to image file
paths inside the EPUB ZIP.

**Rationale**: Image naming conventions vary across publishers.
The first sample EPUB uses `ch2_fig1.jpg` while the second uses
`00002.jpeg`. The XHTML content is the only reliable source for
mapping figure IDs to images, since `<figure>` elements and
their `<img>` tags are standardized in EPUB markup.

**Alternatives considered**:

- Filename-convention matching (`ch{N}_fig{M}`): Only works for
  one publisher's convention. Breaks on sequential naming.
- OPF manifest parsing: The manifest lists all resources but
  doesn't map figure labels to specific images.

### EPUB XHTML Figure Patterns (from samples)

**Pattern A** (The Power of Creative Destruction):

```html
<figure class="IMG">
  <a id="fig2-1"/>
  <img alt="" src="../images/ch2_fig1.jpg"/>
  <figcaption>
    <p class="CAP"><small>FIGURE 2.1.</small> Caption...</p>
  </figcaption>
</figure>
```

**Pattern B** (Loonshots):

```html
<a id="fig161" class="calibre1"></a>
<figure class="img1">
  <img class="img2" src="../images/00041.jpeg" alt=""/>
  <figcaption>
    <p class="caption-cap">Caption text...</p>
  </figcaption>
</figure>
```

### Extraction Algorithm

1. Open EPUB as ZIP, list all `.xhtml` files in `OEBPS/xhtml/`
   or equivalent content directory.
2. For each XHTML file, parse with BeautifulSoup.
3. Find all `<figure>` elements.
4. For each figure, extract:
   - The `<img>` tag's `src` attribute (relative path to image)
   - The `<figcaption>` text to find "FIGURE X.Y." labels
   - Any nearby `<a id="...">` anchor for fallback matching
5. Build a dict: `{"2.1": "OEBPS/images/ch2_fig1.jpg", ...}`
6. For Pattern A: extract label from `<small>FIGURE X.Y.</small>`
7. For Pattern B: extract label from figcaption text if present,
   or fall back to anchor ID parsing

## R2: Figure Reference Detection in Annotations

**Decision**: Use regex to detect two patterns in annotation
text:

1. **Caption pattern**: Text starts with
   `FIGURE\s+(\d+\.\d+[a-z]?)\.?` (case-insensitive)
2. **Inline pattern**: Text contains
   `\(?Figure\s+(\d+\.\d+[a-z]?)\)?` within the body

**Rationale**: Both patterns are observed in the sample data.
Caption annotations contain the full figure caption as the
highlighted text. Inline annotations mention figures
parenthetically within longer passages.

**Alternatives considered**:

- NLP-based entity extraction: Overkill for well-structured
  figure references.
- Only caption detection (skip inline): Would miss common
  references like "(Figure 2.3)" in body text.

## R3: Image Embedding in Annotation Markdown

**Decision**: Add a `figures` field to the Annotation dataclass
(list of figure metadata dicts). The md_writer appends image
links after the annotation text.

**Rationale**: The Annotation dataclass is the shared contract
(Constitution Principle II). Adding an optional field preserves
backward compatibility — existing parsers produce annotations
with an empty figures list. The md_writer renders image links
only when figures are present.

**Alternatives considered**:

- Post-processing the markdown files: Would require re-parsing
  written files. More fragile.
- Separate image metadata file: Adds complexity without benefit.
- Modifying the annotation text directly: Mixes data concerns.

## R4: EPUB Reading Library

**Decision**: Use Python's `zipfile` (stdlib) to read EPUB
archives and BeautifulSoup (`beautifulsoup4`, already a project
dependency) to parse XHTML content.

**Rationale**: No new dependencies needed. EPUB files are
standard ZIP archives. BeautifulSoup is already used by the
Kindle HTML parser, so it's an approved dependency.

**Alternatives considered**:

- `ebooklib`: Third-party EPUB library. Would add a dependency,
  violating Constitution Principle V.
- Manual XML parsing with `xml.etree`: More verbose, less
  tolerant of malformed XHTML.

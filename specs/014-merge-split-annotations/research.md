# Research: Merge Split Zotero Annotations

**Feature**: 014-merge-split-annotations
**Date**: 2026-04-09

## R1: Proximity Detection Strategy

**Decision**: Extract text from PDF pages using pypdf's
`page.extract_text()`, then check if the tail of annotation A
and the head of annotation B appear near each other in the
concatenated text of pages N and N+1.

**Rationale**: pypdf is already a dependency (from feature 013).
Its text extraction is sufficient for substring matching. We
concatenate the text of pages N and N+1, then search for both
annotation texts. If the end position of A's text and the start
position of B's text are within ~10 characters, the annotations
are adjacent in the original document.

**Alternatives considered**:

- Character-level position analysis: pypdf doesn't expose
  character coordinates easily. Substring search is simpler.
- Fuzzy matching: Overkill — exact substring search works
  because annotation text comes directly from the PDF.
- Color matching: Zotero `Annotations.md` doesn't include
  highlight color. Deferred.

## R2: Merge Algorithm

**Decision**: Single-pass scan through parsed annotations.
For each consecutive pair on adjacent pages, check PDF text
proximity. Merge by appending the second annotation's text
(space-separated) to the first. Remove the second annotation.
Support chained merges by continuing to check the next
annotation against the (now-merged) current annotation.

**Rationale**: Simple and efficient. The merge pass runs
once after parsing, before figure extraction and numbering.

### Proximity Check Pseudocode

```text
text_N = pdf.pages[N].extract_text()
text_N1 = pdf.pages[N+1].extract_text()
combined = text_N + " " + text_N1

tail_A = last 30 chars of annotation A text
head_B = first 30 chars of annotation B text

pos_A = combined.rfind(tail_A)
pos_B = combined.find(head_B)

if pos_A >= 0 and pos_B >= 0:
    gap = pos_B - (pos_A + len(tail_A))
    if 0 <= gap <= 10:
        merge A and B
```

## R3: Edge Cases

- Short annotations (< 30 chars): Use the full text for
  matching instead of tail/head substring.
- Text extraction failures: Skip merge for that pair, keep
  both annotations separate.
- Three-way merges: After merging A+B, check if merged
  result should also merge with C.

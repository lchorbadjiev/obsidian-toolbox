# Research: Fix Zotero Word Concatenation

**Feature**: 007-fix-zotero-word-concat
**Date**: 2026-04-06

## R1: aspell Integration Strategy

**Decision**: Use aspell's pipe mode (`aspell -a`) via
`subprocess` for batch word checking and suggestion
retrieval.

**Rationale**: aspell's `list` mode identifies misspelled
words in 9ms for ~4000 unique words. The pipe mode (`-a`)
retrieves suggestions for ~600 misspelled words in ~190ms.
Both are well within the 2-second budget. Using a single
subprocess call for all words avoids per-word process
overhead.

**Approach**:

1. Extract all unique whitespace-delimited tokens from
   annotation text.
2. Run `aspell list` to identify unrecognized words.
3. Run `aspell -a` on unrecognized words to get suggestions.
4. For each word where aspell's first suggestion is a
   space-separated split (e.g., "isthat" → "is that"),
   apply the split.
5. Replace original tokens in the annotation text with
   their split forms.

**Alternatives considered**:

- Per-word subprocess calls: Too slow (~1 process per word).
- Python `aspell` binding (`aspell-python-py3`): Adds a
  dependency; Constitution Principle V prohibits new deps
  without justification. subprocess is sufficient.
- Custom dictionary-based splitting without aspell: Would
  require shipping a word list and reimplementing splitting
  logic that aspell already handles well.

## R2: False Positive Mitigation

**Decision**: Use an allowlist of known technical/compound
words that aspell does not recognize but should not be split.

**Rationale**: aspell flags legitimate words like
"tradeoffs", "superclass", "codebase", "refactorings" as
misspelled and suggests splitting them. These are valid
compound words or domain terms in a software engineering
context.

**Approach**:

1. Maintain a hardcoded set of known compound words that
   should never be split (e.g., "superclass", "subclass",
   "codebase", "tradeoffs", "refactorings").
2. Before applying a split, check if the word (lowercased)
   is in the allowlist; if so, skip it.
3. Additionally, only accept splits where both halves are
   at least 3 characters long to avoid spurious splits
   like "a part" from "apart".
4. Only accept the split if aspell's suggestion contains a
   literal space (not a hyphen), since hyphenated suggestions
   indicate aspell is less confident about a word boundary.

**Alternatives considered**:

- Custom aspell dictionary: More complex setup; users would
  need to install it. Allowlist is simpler.
- Minimum word length threshold only: Insufficient — words
  like "superclass" have long halves but should not be split.

## R3: Mixed-Case Concatenation Handling

**Decision**: Use uppercase boundaries as a secondary
splitting heuristic before falling back to aspell.

**Rationale**: Many concatenation errors in the Zotero
fixture show a pattern like "SoftwareWithout" where the
second word starts with an uppercase letter. aspell handles
these well (suggesting "Software Without"), but the case
boundary provides a strong signal that can also help with
words aspell might not split correctly.

**Approach**: aspell's pipe mode already handles mixed-case
concatenations correctly (e.g., "SoftwareWithout" →
"Software Without"). No special pre-processing is needed;
aspell's suggestions preserve the original casing.

**Alternatives considered**:

- Pre-split on case boundaries before aspell: Would cause
  false positives on camelCase terms like "JavaScript".
  Better to let aspell decide.

## R4: Integration Point in Parse Pipeline

**Decision**: Apply word-splitting as a post-processing step
on the annotation text, after regex extraction but before
`Annotation` object creation.

**Rationale**: The splitting should happen transparently
inside `parse_zotero_annotations()` so that all consumers
(CLI, MCP) get clean text. Processing all annotation texts
in a single aspell batch call is more efficient than
per-annotation calls.

**Approach**:

1. After extracting all annotation texts via regex, collect
   all unique tokens across all annotations.
2. Run aspell once to identify misspelled words and get
   suggestions.
3. Build a replacement map (original → split form).
4. Apply replacements to each annotation text before
   creating `Annotation` objects.

**Alternatives considered**:

- Per-annotation aspell calls: Slower due to subprocess
  overhead multiplied by annotation count.
- Separate CLI command for fixing: Violates the principle
  that parsed output should be clean by default.

## R5: aspell Availability Check

**Decision**: Check for aspell at the start of
`parse_zotero_annotations()` and raise a clear error if
missing.

**Rationale**: aspell is a system dependency, not a Python
package. Users on fresh systems may not have it installed.
A clear error message ("aspell not found. Install it with:
brew install aspell") is better than a cryptic subprocess
error.

**Approach**: Use `shutil.which("aspell")` to check
availability before attempting to call it. Raise a
`RuntimeError` with installation instructions if not found.

**Alternatives considered**:

- Silently skip word-splitting if aspell is missing: Would
  produce degraded output without the user knowing why.
  Explicit failure is better.

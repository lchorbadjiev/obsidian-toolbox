# Data Model: Fix Zotero Word Concatenation

**Feature**: 007-fix-zotero-word-concat
**Date**: 2026-04-06

## Existing Entities (no changes)

### Book

Defined in `src/otb/parser.py`. No modifications needed.

### Annotation

Defined in `src/otb/parser.py`. No modifications needed.
The `text` field will contain cleaned text after
word-splitting is applied during parsing.

## New Internal Structures

### WordFixer (internal, not a dataclass)

A processing unit that takes raw annotation texts and
returns cleaned texts with concatenated words split.

| Concept       | Type             | Description                  |
|---------------|------------------|------------------------------|
| input texts   | list of strings  | Raw annotation texts         |
| misspelled    | set of strings   | Words not in aspell dict     |
| replacements  | mapping str→str  | Original word → split form   |
| allowlist     | set of strings   | Words to never split         |
| output texts  | list of strings  | Cleaned annotation texts     |
| fix count     | integer          | Number of splits performed   |

## Data Flow

```text
Annotations.md ─► regex extraction ─► raw texts
                                         │
                                         ▼
                              collect unique tokens
                                         │
                                         ▼
                              aspell list (misspelled)
                                         │
                                         ▼
                              aspell -a (suggestions)
                                         │
                                         ▼
                              filter: allowlist, min length
                                         │
                                         ▼
                              build replacement map
                                         │
                                         ▼
                              apply replacements to texts
                                         │
                                         ▼
                              Annotation objects (clean text)
```

## Validation Rules

- A word is a candidate for splitting only if:
  1. It is not recognized by aspell (`aspell list`).
  2. It is not in the hardcoded allowlist.
  3. aspell's suggestion contains a space-separated form.
  4. Both halves of the split are at least 3 characters.
- Legitimate English words recognized by aspell are never
  modified.
- The allowlist contains known technical/compound words that
  aspell does not recognize but should not be split.

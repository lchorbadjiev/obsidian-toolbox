# CLI Contract: Zotero Parse (Updated)

**Feature**: 007-fix-zotero-word-concat
**Date**: 2026-04-06

## Command: `otb zotero parse` (updated behavior)

```text
Usage: otb zotero parse [OPTIONS] INPUT_DIR OUTPUT_DIR

  Parse Zotero annotations and write individual markdown
  files.

Arguments:
  INPUT_DIR   Directory containing Annotations.md and
              book.txt
  OUTPUT_DIR  Directory to write annotation markdown files

Options:
  --verbose   Print each word split to stderr
  --help      Show this message and exit.
```

### Updated Behavior

- All existing behavior from 006 is preserved.
- Word concatenation errors in annotation text are
  automatically detected and fixed using aspell before
  writing output files.
- After parsing, prints a summary line to stderr:
  `Fixed N concatenated words in M annotations.`
- With `--verbose`, prints each fix to stderr:
  `'SoftwareWithout' → 'Software Without'`

### Error Conditions

| Condition            | Behavior                           |
|----------------------|------------------------------------|
| aspell not installed | Exit code 1, error message with    |
|                      | installation instructions          |
| aspell failure       | Exit code 1, error on stderr       |

### Exit Codes

| Code | Meaning                             |
|------|-------------------------------------|
| 0    | Success                             |
| 1    | Missing input files, aspell not     |
|      | found, or parse error               |

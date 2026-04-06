# Data Model: Kindle Import Annotations Prompt

**Feature**: 008-kindle-import-prompt
**Date**: 2026-04-06

## Existing Entities (no changes)

### Annotation

Defined in `src/otb/parser.py`. No modifications needed.
The prompt instructs the MCP client to populate the
`title` field on each annotation dict returned by
`parse_kindle_export`.

## Data Flow

```text
User invokes prompt with (file_path)
                │
                ▼
Prompt returns instructions as UserMessage
                │
                ▼
MCP client executes:
  1. parse_kindle_export(file_path)
     → list[dict] with empty titles
                │
                ▼
  2. For each annotation dict:
     Generate title from text (AI subagent)
     Set dict["title"] = generated title
                │
                ▼
  3. save_annotations(annotations, output_dir)
     → list[str] file paths written
```

## No New Entities

This feature adds no new data models. It composes
existing tools (`parse_kindle_export`,
`save_annotations`) with an AI title generation step
orchestrated by the MCP client.

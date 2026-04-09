# MCP Prompt Contract: boox_import_annotations

**Feature**: 012-boox-import-prompt
**Date**: 2026-04-09

## Prompt: `boox_import_annotations`

### Parameters

| Parameter     | Type   | Required | Description                  |
|---------------|--------|----------|------------------------------|
| directory_path | string | yes      | Path to Boox export directory |

### Response

Returns a list containing one `UserMessage` with structured
instructions covering three steps:

1. **Parse**: Call `parse_boox_export(path="{directory_path}")`
2. **Generate titles**: Process annotations in batches of ~30
   using a lightweight model
3. **Save**: Call `save_annotations(annotations=...,
   directory="{output_dir}")` where output_dir is derived as
   `{directory_path}/notes/`

### Instruction Template Structure

```text
Import Boox annotations using this workflow:

**Input directory**: `{directory_path}`
**Output directory**: `{output_dir}/`

## Step 1: Parse the Boox export
Call `parse_boox_export(path="{directory_path}")`.
...

## Step 2: Generate titles
...batches of ~30...lightweight model...

## Step 3: Save annotations
Call `save_annotations(annotations=..., directory="...")`.
...

## Expected result
Report the number of files written and output directory.
```

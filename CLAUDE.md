# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
uv sync          # install / update dependencies
uv run otb       # run the CLI
uv run pytest    # run tests
```

## Architecture

`src/otb/` — package root using a `src` layout.  
`src/otb/cli.py:main` — CLI entrypoint, registered as the `otb` script in `pyproject.toml`.

Add CLI sub-commands in `cli.py` or split into modules under `src/otb/` and import them there.

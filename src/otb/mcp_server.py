"""MCP server for obsidian-toolbox.

Exposes three tools:
- parse_kindle_export: parse a Kindle HTML notebook export into raw highlights
- parse_md_highlights_dir: read a directory of markdown highlight files
- save_highlights: write highlights as individual markdown files
"""
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from otb.md_parser import parse_highlight_md
from otb.md_writer import write_highlights
from otb.parser import Book, Highlight, parse_notebook

mcp = FastMCP(
    "obsidian-toolbox",
    instructions=(
        "Use parse_kindle_export to get highlights from a Kindle export file. "
        "The returned highlights have no titles. Before calling save_highlights, "
        "generate a concise title (under 10 words) for each highlight using the "
        "highlight text, then include it in the 'title' field when saving."
    ),
)


def _highlight_to_dict(h: Highlight) -> dict[str, Any]:
    return {
        "book_title": h.book.title,
        "author": h.book.author,
        "chapter": h.chapter,
        "page": h.page,
        "location": h.location,
        "text": h.text,
        "title": h.title,
        "color": h.color,
        "number": h.number,
    }


def _dict_to_highlight(d: dict[str, Any]) -> Highlight:
    return Highlight(
        book=Book(title=str(d["book_title"]), author=str(d["author"])),
        chapter=str(d.get("chapter", "")),
        page=int(d.get("page", 0)),
        location=int(d.get("location", 0)),
        text=str(d["text"]),
        title=str(d.get("title", "")),
        color=str(d["color"]) if d.get("color") is not None else None,
        number=int(d.get("number", 0)),
    )


@mcp.tool(
    description=(
        "Parse a Kindle HTML notebook export and return all highlights as a list. "
        "Each highlight has: book_title, author, chapter, page, location, text, "
        "color, number, and title (always empty — generate titles yourself before "
        "saving). "
        "Raises FileNotFoundError if the path does not exist."
    )
)
def parse_kindle_export(path: str) -> list[dict[str, Any]]:
    """Return highlights from a Kindle HTML export. Titles are always empty."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {path}")
    highlights = parse_notebook(resolved, generate_title=False)
    return [_highlight_to_dict(h) for h in highlights]


@mcp.tool(
    description=(
        "Read all highlight markdown files in a directory and return them as a list. "
        "Files are returned in filename-sorted order. "
        "Returns {highlights: [...], parse_errors: {filename: error_message}}. "
        "parse_errors is empty when all files parse successfully; malformed files are "
        "skipped and reported there without aborting the call. "
        "Raises FileNotFoundError if the path does not exist, "
        "NotADirectoryError if the path is a file."
    )
)
def parse_md_highlights_dir(
    directory: str,
) -> dict[str, Any]:
    """Return highlights from all .md files in directory; report per-file errors."""
    resolved = Path(directory)
    if not resolved.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    highlights: list[dict[str, Any]] = []
    parse_errors: dict[str, str] = {}
    for md_file in sorted(resolved.glob("*.md")):
        try:
            h = parse_highlight_md(md_file)
            highlights.append(_highlight_to_dict(h))
        except Exception as exc:  # pylint: disable=broad-exception-caught  # per-file tolerance: report and continue
            parse_errors[md_file.name] = str(exc)
    return {"highlights": highlights, "parse_errors": parse_errors}


@mcp.tool(
    description=(
        "Save a list of highlights as individual markdown files in the given directory. "
        "The directory is created if it does not exist. "
        "Each highlight dict must have: book_title, author, chapter, page, location, "
        "text, number. Optional fields: title (str), color (str or null). "
        "Returns the list of file paths written."
    )
)
def save_highlights(highlights: list[dict[str, Any]], directory: str) -> list[str]:
    """Write each highlight to a markdown file; return the paths created."""
    target = Path(directory)
    objects = [_dict_to_highlight(d) for d in highlights]
    paths = write_highlights(objects, target)
    return [str(p) for p in paths]


def run() -> None:
    """Start the MCP server using stdio transport."""
    mcp.run(transport="stdio")

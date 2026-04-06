"""MCP server for obsidian-toolbox.

Exposes three tools and one prompt:
- parse_kindle_export: parse a Kindle HTML notebook export
- parse_md_annotations_dir: read a directory of annotation markdown files
- save_annotations: write annotations as individual markdown files
- generate_book_index: prompt to generate a book index markdown file
"""
from collections import defaultdict
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts.base import UserMessage

from otb.anki import export_annotations
from otb.md_parser import parse_annotation_dir_with_paths, parse_annotation_md
from otb.md_writer import write_annotations
from otb.parser import Annotation, Book, parse_notebook
from otb.zotero_parser import parse_zotero_annotations

mcp = FastMCP(
    "obsidian-toolbox",
    instructions=(
        "Use parse_kindle_export to get annotations from a Kindle export file. "
        "The returned annotations have no titles. Before calling save_annotations, "
        "generate a concise title (under 10 words) for each annotation using the "
        "annotation text, then include it in the 'title' field when saving."
    ),
)


def _annotation_to_dict(a: Annotation) -> dict[str, Any]:
    return {
        "book_title": a.book.title,
        "author": a.book.author,
        "chapter": a.chapter,
        "page": a.page,
        "location": a.location,
        "text": a.text,
        "title": a.title,
        "color": a.color,
        "number": a.number,
    }


def _dict_to_annotation(d: dict[str, Any]) -> Annotation:
    return Annotation(
        book=Book(title=str(d["book_title"]), author=str(d["author"])),
        chapter=str(d.get("chapter", "")),
        page=str(d.get("page", "")),
        location=int(d.get("location", 0)),
        text=str(d["text"]),
        title=str(d.get("title", "")),
        color=str(d["color"]) if d.get("color") is not None else None,
        number=int(d.get("number", 0)),
    )


@mcp.tool(
    description=(
        "Parse a Kindle HTML notebook export and return all annotations as a list. "
        "Each annotation has: book_title, author, chapter, page, location, text, "
        "color, number, and title (always empty — generate titles yourself before "
        "saving). "
        "Raises FileNotFoundError if the path does not exist."
    )
)
def parse_kindle_export(path: str) -> list[dict[str, Any]]:
    """Return annotations from a Kindle HTML export. Titles are always empty."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"File not found: {path}")
    annotations = parse_notebook(resolved, generate_title=False)
    return [_annotation_to_dict(a) for a in annotations]


@mcp.tool(
    description=(
        "Read all annotation markdown files in a directory and return them as a list. "
        "Files are returned in filename-sorted order. "
        "Returns {annotations: [...], parse_errors: {filename: error_message}}. "
        "parse_errors is empty when all files parse successfully; malformed files are "
        "skipped and reported there without aborting the call. "
        "Raises FileNotFoundError if the path does not exist, "
        "NotADirectoryError if the path is a file."
    )
)
def parse_md_annotations_dir(
    directory: str,
) -> dict[str, Any]:
    """Return annotations from all .md files in directory; report per-file errors."""
    resolved = Path(directory)
    if not resolved.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {directory}")
    annotations: list[dict[str, Any]] = []
    parse_errors: dict[str, str] = {}
    for md_file in sorted(resolved.glob("*.md")):
        try:
            a = parse_annotation_md(md_file)
            annotations.append(_annotation_to_dict(a))
        except Exception as exc:  # pylint: disable=broad-exception-caught  # per-file tolerance: report and continue
            parse_errors[md_file.name] = str(exc)
    return {"annotations": annotations, "parse_errors": parse_errors}


@mcp.tool(
    description=(
        "Save a list of annotations as individual markdown files in the given directory. "
        "The directory is created if it does not exist. "
        "Each annotation dict must have: book_title, author, chapter, page, location, "
        "text, number. Optional fields: title (str), color (str or null). "
        "Returns the list of file paths written."
    )
)
def save_annotations(annotations: list[dict[str, Any]], directory: str) -> list[str]:
    """Write each annotation to a markdown file; return the paths created."""
    target = Path(directory)
    objects = [_dict_to_annotation(d) for d in annotations]
    paths = write_annotations(objects, target)
    return [str(p) for p in paths]


def _build_index_prompt(  # pylint: disable=too-many-locals  # prompt builder collects book/chapter/annotation state in a single pass
    directory: str,
) -> str:
    """Build the book index generation prompt text from an annotations dir."""
    resolved = Path(directory)
    if not resolved.exists():
        return f"Error: directory not found: {directory}"
    if not resolved.is_dir():
        return f"Error: path is not a directory: {directory}"

    annotations: list[Annotation] = []
    skipped: list[str] = []
    for md_file in sorted(resolved.glob("*.md")):
        try:
            annotations.append(parse_annotation_md(md_file))
        except Exception as exc:  # pylint: disable=broad-exception-caught  # per-file tolerance
            skipped.append(f"{md_file.name}: {exc}")

    if not annotations:
        msg = "No valid annotation files found in the directory."
        if skipped:
            msg += " Skipped files:\n" + "\n".join(f"  - {s}" for s in skipped)
        return msg

    first = annotations[0]
    book_title = first.book.title
    author = first.book.author

    # Group by chapter (preserve filename-sorted order within each group)
    chapters: dict[str, list[Annotation]] = defaultdict(list)
    for a in annotations:
        chapters[a.chapter].append(a)

    lines: list[str] = [
        f'You have {len(annotations)} annotations from "{book_title}" by {author}.',
        "",
        "Generate a book index markdown file in this exact format:",
        "",
        "```markdown",
        "---",
        "tags: [book]",
        f"author: {author}",
        "published: <year if known, otherwise leave blank>",
        "---",
        "",
        f"# {book_title}",
        "",
        "<2–4 paragraph prose summary of the book's main argument,",
        " themes, and significance, written in your own words>",
        "",
        "---",
        "",
        "## Notes by Chapter",
        "",
        "<one ### subsection per chapter, each containing wikilinks>",
        "```",
        "",
        "Use this wikilink format for each note:",
        "  [[notes/NNN - Title of Note]]",
        "where NNN is the zero-padded annotation number (e.g. 001).",
        "",
        "---",
        "",
        "## Annotations by Chapter",
        "",
    ]

    for chapter, chapter_annotations in chapters.items():
        lines.append(f"### {chapter}")
        lines.append("")
        for a in chapter_annotations:
            num = f"{a.number:03d}"
            lines.append(f"**{num} — {a.title}**")
            lines.append(f"Wikilink: [[notes/{num} - {a.title}]]")
            lines.append(f"> {a.text}")
            lines.append("")

    if skipped:
        lines.append("---")
        lines.append("")
        lines.append("The following files were skipped due to parse errors:")
        for s in skipped:
            lines.append(f"  - {s}")
        lines.append("")

    return "\n".join(lines)


@mcp.prompt(
    description=(
        "Generate a book index markdown file from a directory of annotation "
        "markdown files. Returns a prompt containing all annotation data grouped "
        "by chapter with wikilinks and instructions to produce frontmatter, a "
        "prose summary, and a Notes by Chapter section."
    )
)
def generate_book_index(directory: str) -> list[UserMessage]:
    """Return a prompt for generating a book index from an annotations dir."""
    return [UserMessage(content=_build_index_prompt(directory))]


@mcp.tool(
    description=(
        "Export book annotations from a directory of annotation markdown files "
        "to an Anki deck via AnkiConnect. "
        "Each annotation becomes one Basic card: front = chapter + title, "
        "back = full annotation text. "
        "After successful creation, the Anki note ID is written back to each "
        "annotation file as the anki_id frontmatter field. "
        "Annotations with anki_id already set are verified against Anki and "
        "skipped if the note still exists. "
        "Returns {created, skipped, failed} counts. "
        "Raises FileNotFoundError if path does not exist, "
        "NotADirectoryError if path is a file, "
        "AnkiConnectError if Anki is unreachable."
    )
)
def anki_export(
    path: str,
    deck: str = "",
    anki_url: str = "http://localhost:8765",
) -> dict[str, Any]:
    """Export annotation markdown files to Anki; return created/skipped/failed."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    annotated_paths = parse_annotation_dir_with_paths(resolved)
    if not annotated_paths:
        return {"created": 0, "skipped": 0, "failed": 0}
    resolved_deck = deck or annotated_paths[0][1].book.title
    result = export_annotations(annotated_paths, deck=resolved_deck, anki_url=anki_url)
    return {"created": result.created, "skipped": result.skipped, "failed": result.failed}


@mcp.tool(
    description=(
        "Parse a Zotero annotation export directory and return all annotations "
        "as a list. The directory must contain Annotations.md and book.txt. "
        "Each annotation has: book_title, author, chapter, page, location, text, "
        "title (auto-generated), color (always null), number. "
        "Raises FileNotFoundError if the directory or required files do not exist. "
        "Raises NotADirectoryError if the path is not a directory."
    )
)
def parse_zotero_export(path: str) -> list[dict[str, Any]]:
    """Return annotations from a Zotero export directory."""
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Directory not found: {path}")
    if not resolved.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {path}")
    annotations = parse_zotero_annotations(resolved)
    return [_annotation_to_dict(a) for a in annotations]


@mcp.prompt(
    description=(
        "Import Kindle annotations from an HTML export file. "
        "Orchestrates: parse annotations, generate titles using a "
        "lightweight AI model, and save as individual markdown files. "
        "Returns step-by-step instructions for the MCP client to execute."
    )
)
def kindle_import_annotations(
    file_path: str,
) -> list[UserMessage]:
    """Return instructions to import Kindle annotations."""
    output_dir = str(Path(file_path).parent / "notes")
    text = (
        "Import Kindle annotations using this workflow:\n"
        "\n"
        f"**Input file**: `{file_path}`\n"
        f"**Output directory**: `{output_dir}/`\n"
        "\n"
        "## Step 1: Parse the Kindle export\n"
        "\n"
        f'Call `parse_kindle_export(path="{file_path}")`.\n'
        "This returns a list of annotation dicts, each with "
        "an empty `title` field.\n"
        "\n"
        "## Step 2: Generate titles\n"
        "\n"
        "For each annotation in the list, generate a concise "
        "title (under 10 words) from the annotation `text` "
        "field. Use a lightweight model (e.g. Haiku) as a "
        "subagent for speed. Set the `title` field on each "
        "annotation dict.\n"
        "\n"
        "If title generation fails for any annotation, fall "
        "back to the first 7 words of the text, title-cased.\n"
        "\n"
        "## Step 3: Save annotations\n"
        "\n"
        "Call `save_annotations(annotations=<the list with "
        f'titles>, directory="{output_dir}")`.\n'
        "This writes one markdown file per annotation.\n"
        "\n"
        "## Expected result\n"
        "\n"
        "Report the number of files written and the output "
        "directory path."
    )
    return [UserMessage(content=text)]


def run() -> None:
    """Start the MCP server using stdio transport."""
    mcp.run(transport="stdio")

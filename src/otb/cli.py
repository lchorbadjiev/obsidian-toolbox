"""CLI entrypoint for obsidian-toolbox."""
import sys
from pathlib import Path

import click

from otb.anki import AnkiConnectError, export_annotations
from otb.md_parser import parse_annotation_dir, parse_annotation_dir_with_paths
from otb.md_writer import write_annotations
from otb.mcp_server import _build_index_prompt, run as mcp_run
from otb.parser import parse_notebook
from otb.boox_parser import parse_boox_annotations
from otb.zotero_parser import parse_zotero_annotations


@click.group()
@click.version_option(package_name="obsidian-toolbox")
def main() -> None:
    """Obsidian Toolbox."""


@main.group()
def kindle() -> None:
    """Commands for Kindle notebook exports."""


@main.command("mcp")
def mcp_serve() -> None:
    """Start the MCP server using stdio transport."""
    mcp_run()


@main.group()
def md() -> None:
    """Commands for annotation markdown files."""


@md.command("count")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path))
def md_count(path: Path) -> None:
    """Print the number of annotations in a directory of annotation markdown files."""
    click.echo(len(parse_annotation_dir(path)))


@md.command("index-prompt")
@click.argument("path", type=click.Path(exists=True, file_okay=False, path_type=Path))
def md_index_prompt(path: Path) -> None:
    """Print the book index generation prompt for an annotations directory."""
    click.echo(_build_index_prompt(str(path)))


@kindle.command("count")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def kindle_count(path: Path) -> None:
    """Print the number of annotations in a Kindle notebook HTML export."""
    annotations = parse_notebook(path)
    click.echo(len(annotations))


@main.group()
def anki() -> None:
    """Commands for Anki flashcard export."""


@anki.command("export")
@click.argument(
    "path",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.option("--deck", default="", help="Target Anki deck name (default: book title).")
@click.option(
    "--anki-url",
    default="http://localhost:8765",
    help="AnkiConnect base URL.",
    show_default=True,
)
def anki_export_cmd(path: Path, deck: str, anki_url: str) -> None:
    """Export annotation markdown files in PATH to an Anki deck."""
    annotated_paths = parse_annotation_dir_with_paths(path)
    if not annotated_paths:
        click.echo("No annotations found.", err=True)
        sys.exit(1)
    resolved_deck = deck or annotated_paths[0][1].book.title
    try:
        result = export_annotations(annotated_paths, deck=resolved_deck, anki_url=anki_url)
    except AnkiConnectError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    click.echo(f"Created: {result.created}  Skipped: {result.skipped}  Failed: {result.failed}")


@main.group()
def boox() -> None:
    """Commands for Boox annotation exports."""


@boox.command("parse")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path))
def boox_parse(input_dir: Path, output_dir: Path) -> None:
    """Parse Boox annotations and write individual markdown files."""
    try:
        annotations = parse_boox_annotations(input_dir)
    except FileNotFoundError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    write_annotations(annotations, output_dir)
    click.echo(len(annotations))


@main.group()
def zotero() -> None:
    """Commands for Zotero annotation exports."""


@zotero.command("parse")
@click.argument("input_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.argument("output_dir", type=click.Path(file_okay=False, path_type=Path))
@click.option("--verbose", is_flag=True, help="Print each word split to stderr.")
def zotero_parse(input_dir: Path, output_dir: Path, verbose: bool) -> None:
    """Parse Zotero annotations and write individual markdown files."""
    try:
        annotations = parse_zotero_annotations(input_dir, verbose=verbose)
    except (FileNotFoundError, RuntimeError) as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
    write_annotations(annotations, output_dir)
    click.echo(len(annotations))

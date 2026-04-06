"""CLI entrypoint for obsidian-toolbox."""
from pathlib import Path

import click

from otb.md_parser import parse_annotation_dir
from otb.mcp_server import _build_index_prompt, run as mcp_run
from otb.parser import parse_notebook


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

"""CLI entrypoint for obsidian-toolbox."""
from pathlib import Path

import click

from otb.parser import parse_notebook


@click.group()
@click.version_option(package_name="obsidian-toolbox")
def main() -> None:
    """Obsidian Toolbox."""


@main.group()
def kindle() -> None:
    """Commands for Kindle notebook exports."""


@kindle.command("count")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def kindle_count(path: Path) -> None:
    """Print the number of highlights in a Kindle notebook HTML export."""
    highlights = parse_notebook(path)
    click.echo(len(highlights))

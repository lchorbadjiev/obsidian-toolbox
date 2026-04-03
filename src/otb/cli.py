"""CLI entrypoint for obsidian-toolbox."""
import click


@click.group()
@click.version_option(package_name="obsidian-toolbox")
def main() -> None:
    """Obsidian Toolbox."""

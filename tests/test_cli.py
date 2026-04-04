"""Tests for the CLI entrypoint."""
# pylint: disable=missing-function-docstring
from pathlib import Path

from click.testing import CliRunner

from otb.cli import main

NOTEBOOK_FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"


def test_help() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0


def test_version() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_kindle_count() -> None:
    result = CliRunner().invoke(main, ["kindle", "count", str(NOTEBOOK_FIXTURE)])
    assert result.exit_code == 0
    assert result.output.strip() == "4"

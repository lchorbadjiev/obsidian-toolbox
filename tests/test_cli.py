"""Tests for the CLI entrypoint."""
# pylint: disable=missing-function-docstring
from click.testing import CliRunner

from otb.cli import main


def test_help() -> None:
    result = CliRunner().invoke(main, ["--help"])
    assert result.exit_code == 0


def test_version() -> None:
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output

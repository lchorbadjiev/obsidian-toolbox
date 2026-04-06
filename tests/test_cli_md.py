# pylint: disable=missing-function-docstring
"""Tests for the otb md CLI command group."""
from pathlib import Path

from click.testing import CliRunner

from otb.cli import main

MD_FIXTURES = Path(__file__).parent / "fixtures" / "annotations"


def test_md_count_valid_dir() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["md", "count", str(MD_FIXTURES)])
    assert result.exit_code == 0
    assert result.output.strip() == "4"


def test_md_count_empty_dir(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["md", "count", str(tmp_path)])
    assert result.exit_code == 0
    assert result.output.strip() == "0"


def test_md_count_nonexistent_path() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["md", "count", "/tmp/no_such_dir_xyz"])
    assert result.exit_code != 0


def test_md_index_prompt_valid_dir() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["md", "index-prompt", str(MD_FIXTURES)])
    assert result.exit_code == 0
    assert "A Brief History of Time" in result.output


def test_md_index_prompt_nonexistent_path() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main, ["md", "index-prompt", "/tmp/no_such_dir_xyz"]
    )
    assert result.exit_code != 0

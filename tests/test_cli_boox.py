"""Tests for the Boox CLI commands."""
# pylint: disable=missing-function-docstring
from pathlib import Path

from click.testing import CliRunner

from otb.cli import main
from otb.md_parser import parse_annotation_dir

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "boox"


# ---------------------------------------------------------------------------
# CLI happy path
# ---------------------------------------------------------------------------


def test_boox_parse_happy_path(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["boox", "parse", str(FIXTURE_DIR), str(out_dir)]
    )
    assert result.exit_code == 0
    md_files = list(out_dir.glob("*.md"))
    assert len(md_files) == 35


# ---------------------------------------------------------------------------
# CLI round-trip (output parseable by md_parser)
# ---------------------------------------------------------------------------


def test_boox_parse_round_trip(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    CliRunner().invoke(
        main, ["boox", "parse", str(FIXTURE_DIR), str(out_dir)]
    )
    annotations = parse_annotation_dir(out_dir)
    assert len(annotations) == 35
    assert annotations[0].book.title == (
        "Just for Fun: The Story of an Accidental Revolutionary"
    )


# ---------------------------------------------------------------------------
# CLI missing book.txt -> exit code 1
# ---------------------------------------------------------------------------


def test_boox_parse_missing_book_txt(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ann = input_dir / "annotations.txt"
    ann.write_text("Reading Notes | <<Test>>Author\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["boox", "parse", str(input_dir), str(out_dir)]
    )
    assert result.exit_code == 1

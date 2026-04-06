"""Tests for the Zotero CLI commands."""
# pylint: disable=missing-function-docstring
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from otb.cli import main
from otb.md_parser import parse_annotation_dir

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "zotero"


# ---------------------------------------------------------------------------
# T009: CLI happy path
# ---------------------------------------------------------------------------


def test_zotero_parse_happy_path(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["zotero", "parse", str(FIXTURE_DIR), str(out_dir)]
    )
    assert result.exit_code == 0
    md_files = list(out_dir.glob("*.md"))
    assert len(md_files) == 306


# ---------------------------------------------------------------------------
# T010: CLI round-trip (output parseable by md_parser)
# ---------------------------------------------------------------------------


def test_zotero_parse_round_trip(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    CliRunner().invoke(
        main, ["zotero", "parse", str(FIXTURE_DIR), str(out_dir)]
    )
    annotations = parse_annotation_dir(out_dir)
    assert len(annotations) == 306
    assert annotations[0].book.title == (
        "Refactoring: Improving the Design of Existing Code"
    )


# ---------------------------------------------------------------------------
# T011: CLI missing book.txt -> exit code 1
# ---------------------------------------------------------------------------


def test_zotero_parse_missing_book_txt(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    ann_md = input_dir / "Annotations.md"
    ann_md.write_text("# Annotations\n(date)\n", encoding="utf-8")
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["zotero", "parse", str(input_dir), str(out_dir)]
    )
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# T014: CLI prints fix count summary on stderr
# ---------------------------------------------------------------------------


def test_zotero_parse_fix_count_summary(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["zotero", "parse", str(FIXTURE_DIR), str(out_dir)]
    )
    assert result.exit_code == 0
    assert "Fixed" in result.output


# ---------------------------------------------------------------------------
# T015: CLI aspell not found
# ---------------------------------------------------------------------------


def test_zotero_parse_aspell_not_found(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    with patch("otb.word_fixer.shutil.which", return_value=None):
        result = CliRunner().invoke(
            main, ["zotero", "parse", str(FIXTURE_DIR), str(out_dir)]
        )
    assert result.exit_code == 1
    assert "aspell" in result.output


# ---------------------------------------------------------------------------
# T020: CLI --verbose flag
# ---------------------------------------------------------------------------


def test_zotero_parse_verbose(tmp_path: Path) -> None:
    out_dir = tmp_path / "output"
    result = CliRunner().invoke(
        main,
        ["zotero", "parse", "--verbose", str(FIXTURE_DIR), str(out_dir)],
    )
    assert result.exit_code == 0
    assert "\u2192" in result.output  # arrow in verbose split reports

"""Tests for the CLI entrypoint."""
# pylint: disable=missing-function-docstring
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from otb.anki import AnkiConnectError, ExportResult
from otb.cli import main

NOTEBOOK_FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"
ANNOTATIONS_DIR = Path(__file__).parent / "fixtures" / "annotations"


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


# ---------------------------------------------------------------------------
# otb anki export
# ---------------------------------------------------------------------------


def _make_export_result(created: int = 4, skipped: int = 0, failed: int = 0) -> ExportResult:
    return ExportResult(created=created, skipped=skipped, failed=failed)


def test_anki_export_happy_path() -> None:
    with patch("otb.cli.export_annotations", return_value=_make_export_result(4)):
        result = CliRunner().invoke(main, ["anki", "export", str(ANNOTATIONS_DIR)])
    assert result.exit_code == 0
    assert "Created: 4" in result.output
    assert "Skipped: 0" in result.output
    assert "Failed: 0" in result.output


def test_anki_export_non_directory_rejected(tmp_path: Path) -> None:
    f = tmp_path / "file.txt"
    f.write_text("x", encoding="utf-8")
    result = CliRunner().invoke(main, ["anki", "export", str(f)])
    assert result.exit_code != 0


def test_anki_export_unreachable_exits_nonzero() -> None:
    with patch(
        "otb.cli.export_annotations",
        side_effect=AnkiConnectError("Connection refused"),
    ):
        result = CliRunner().invoke(main, ["anki", "export", str(ANNOTATIONS_DIR)])
    assert result.exit_code != 0
    assert "Cannot connect" in result.output or "Connection refused" in result.output


def test_anki_export_custom_deck() -> None:
    with patch("otb.cli.export_annotations", return_value=_make_export_result()) as mock_exp:
        CliRunner().invoke(
            main, ["anki", "export", str(ANNOTATIONS_DIR), "--deck", "My::Deck"]
        )
    _, kwargs = mock_exp.call_args
    assert kwargs.get("deck") == "My::Deck" or mock_exp.call_args[0][1] == "My::Deck"


def test_anki_export_custom_url() -> None:
    with patch("otb.cli.export_annotations", return_value=_make_export_result()) as mock_exp:
        CliRunner().invoke(
            main,
            ["anki", "export", str(ANNOTATIONS_DIR), "--anki-url", "http://localhost:9999"],
        )
    args = mock_exp.call_args
    flat = list(args[0]) + list(args[1].values())
    assert "http://localhost:9999" in flat

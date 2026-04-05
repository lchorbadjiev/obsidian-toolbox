# pylint: disable=missing-function-docstring
"""Tests for the MCP server tool handlers."""
from pathlib import Path

import stat
import sys

import pytest

from otb.mcp_server import parse_kindle_export, save_highlights

FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"


def test_parse_returns_highlights() -> None:
    result = parse_kindle_export(str(FIXTURE))
    assert len(result) == 4


def test_parse_no_titles() -> None:
    result = parse_kindle_export(str(FIXTURE))
    assert all(h["title"] == "" for h in result)


def test_parse_highlight_fields() -> None:
    result = parse_kindle_export(str(FIXTURE))
    h = result[0]
    assert h["book_title"] == "A Brief History of Time"
    assert h["author"] == "Stephen Hawking"
    assert h["chapter"] == "1   Our Picture of the Universe"
    assert h["page"] == 1
    assert h["location"] == 42
    assert h["text"] == "A well-known scientist once gave a public lecture on astronomy."
    assert h["color"] == "yellow"
    assert h["number"] == 1


def test_parse_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        parse_kindle_export("/tmp/does_not_exist.html")


def test_parse_empty_export(tmp_path: Path) -> None:
    # Minimal valid HTML with no highlights
    empty_html = tmp_path / "empty.html"
    empty_html.write_text(
        """<html><body>
        <div class="bookTitle">Empty Book</div>
        <div class="authors">Smith, John</div>
        <div class="bodyContainer"></div>
        </body></html>""",
        encoding="utf-8",
    )
    result = parse_kindle_export(str(empty_html))
    assert result == []


# --- save_highlights tool ---

def test_save_returns_paths(tmp_path: Path) -> None:
    highlights = parse_kindle_export(str(FIXTURE))
    for h in highlights:
        h["title"] = "Generated Title"
    paths = save_highlights(highlights, str(tmp_path / "out"))
    assert len(paths) == 4
    assert all(Path(p).exists() for p in paths)


def test_save_creates_directory(tmp_path: Path) -> None:
    target = str(tmp_path / "new" / "subdir")
    highlights = parse_kindle_export(str(FIXTURE))
    paths = save_highlights(highlights[:1], target)
    assert Path(paths[0]).exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
def test_save_non_writable_directory_raises(tmp_path: Path) -> None:
    target = tmp_path / "readonly"
    target.mkdir()
    target.chmod(stat.S_IRUSR | stat.S_IXUSR)
    highlights = parse_kindle_export(str(FIXTURE))
    try:
        with pytest.raises(OSError):
            save_highlights(highlights[:1], str(target))
    finally:
        target.chmod(stat.S_IRWXU)

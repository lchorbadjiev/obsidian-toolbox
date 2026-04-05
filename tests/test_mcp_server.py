# pylint: disable=missing-function-docstring,use-implicit-booleaness-not-comparison
"""Tests for the MCP server tool handlers."""
import shutil
from pathlib import Path

import stat
import sys

import pytest

from otb.mcp_server import (
    generate_book_index,
    parse_kindle_export,
    parse_md_highlights_dir,
    save_highlights,
)

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


# --- parse_md_highlights_dir tool ---

MD_FIXTURES = Path(__file__).parent / "fixtures" / "highlights"


def test_parse_md_dir_returns_highlights() -> None:
    result = parse_md_highlights_dir(str(MD_FIXTURES))
    assert result["highlights"] != [] and len(result["highlights"]) == 4


def test_parse_md_dir_sorted_order() -> None:
    result = parse_md_highlights_dir(str(MD_FIXTURES))
    numbers = [h["number"] for h in result["highlights"]]
    assert numbers == sorted(numbers)


def test_parse_md_dir_highlight_fields() -> None:
    result = parse_md_highlights_dir(str(MD_FIXTURES))
    h = result["highlights"][0]
    assert h["book_title"] == "A Brief History of Time"
    assert h["author"] == "Stephen Hawking"
    assert "text" in h
    assert "chapter" in h
    assert "page" in h
    assert "location" in h
    assert "number" in h


def test_parse_md_dir_no_parse_errors() -> None:
    result = parse_md_highlights_dir(str(MD_FIXTURES))
    assert result["parse_errors"] == {}


def test_parse_md_dir_empty_directory(tmp_path: Path) -> None:
    result = parse_md_highlights_dir(str(tmp_path))
    assert result["highlights"] == []
    assert result["parse_errors"] == {}


def test_parse_md_dir_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        parse_md_highlights_dir("/tmp/no_such_dir_xyz")


def test_parse_md_dir_file_not_directory(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir.md"
    f.write_text("content", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        parse_md_highlights_dir(str(f))


def test_parse_md_dir_malformed_file_reported(tmp_path: Path) -> None:
    # Copy a valid fixture then add a malformed file
    for src in MD_FIXTURES.glob("*.md"):
        shutil.copy(src, tmp_path / src.name)
    bad = tmp_path / "000 - bad.md"
    bad.write_text("no frontmatter here", encoding="utf-8")
    result = parse_md_highlights_dir(str(tmp_path))
    assert len(result["highlights"]) == 4
    assert "000 - bad.md" in result["parse_errors"]


# --- generate_book_index prompt ---


def test_generate_book_index_returns_message() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    assert len(result) == 1
    assert result[0].role == "user"
    text = result[0].content.text
    assert "A Brief History of Time" in text
    assert "Stephen Hawking" in text


def test_generate_book_index_contains_highlights() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    text = result[0].content.text
    # All 4 highlight titles should appear in the prompt
    assert "A Well-Known Scientist" in text
    assert "Any Physical Theory" in text


def test_generate_book_index_wikilinks() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    text = result[0].content.text
    assert "[[notes/001 - " in text


def test_generate_book_index_chapter_grouping() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    text = result[0].content.text
    assert "Our Picture of the Universe" in text


def test_generate_book_index_missing_path() -> None:
    result = generate_book_index("/tmp/no_such_dir_xyz_abc")
    assert len(result) == 1
    assert result[0].role == "user"
    text = result[0].content.text
    assert "error" in text.lower() or "not found" in text.lower()


def test_generate_book_index_file_not_dir(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir.md"
    f.write_text("content", encoding="utf-8")
    result = generate_book_index(str(f))
    assert len(result) == 1
    text = result[0].content.text
    assert "error" in text.lower() or "not a directory" in text.lower()


def test_generate_book_index_empty_dir(tmp_path: Path) -> None:
    result = generate_book_index(str(tmp_path))
    assert len(result) == 1
    text = result[0].content.text
    assert len(text) > 0


def test_generate_book_index_malformed_skipped(tmp_path: Path) -> None:
    for src in MD_FIXTURES.glob("*.md"):
        shutil.copy(src, tmp_path / src.name)
    bad = tmp_path / "000 - bad.md"
    bad.write_text("no frontmatter here", encoding="utf-8")
    result = generate_book_index(str(tmp_path))
    text = result[0].content.text
    assert "A Brief History of Time" in text
    assert "000 - bad.md" in text

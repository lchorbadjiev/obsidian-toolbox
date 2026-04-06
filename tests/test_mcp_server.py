# pylint: disable=missing-function-docstring,use-implicit-booleaness-not-comparison
"""Tests for the MCP server tool handlers."""
import shutil
import stat
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from otb.anki import AnkiConnectError, ExportResult
from otb.mcp_server import (
    anki_export,
    generate_book_index,
    kindle_import_annotations,
    parse_kindle_export,
    parse_md_annotations_dir,
    parse_zotero_export,
    save_annotations,
)

FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"


def test_parse_returns_annotations() -> None:
    result = parse_kindle_export(str(FIXTURE))
    assert len(result) == 4


def test_parse_no_titles() -> None:
    result = parse_kindle_export(str(FIXTURE))
    assert all(a["title"] == "" for a in result)


def test_parse_annotation_fields() -> None:
    result = parse_kindle_export(str(FIXTURE))
    a = result[0]
    assert a["book_title"] == "A Brief History of Time"
    assert a["author"] == "Stephen Hawking"
    assert a["chapter"] == "1   Our Picture of the Universe"
    assert a["page"] == "1"
    assert a["location"] == 42
    assert a["text"] == "A well-known scientist once gave a public lecture on astronomy."
    assert a["color"] == "yellow"
    assert a["number"] == 1


def test_parse_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        parse_kindle_export("/tmp/does_not_exist.html")


def test_parse_empty_export(tmp_path: Path) -> None:
    # Minimal valid HTML with no annotations
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


# --- save_annotations tool ---

def test_save_returns_paths(tmp_path: Path) -> None:
    annotations = parse_kindle_export(str(FIXTURE))
    for a in annotations:
        a["title"] = "Generated Title"
    paths = save_annotations(annotations, str(tmp_path / "out"))
    assert len(paths) == 4
    assert all(Path(p).exists() for p in paths)


def test_save_creates_directory(tmp_path: Path) -> None:
    target = str(tmp_path / "new" / "subdir")
    annotations = parse_kindle_export(str(FIXTURE))
    paths = save_annotations(annotations[:1], target)
    assert Path(paths[0]).exists()


@pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
def test_save_non_writable_directory_raises(tmp_path: Path) -> None:
    target = tmp_path / "readonly"
    target.mkdir()
    target.chmod(stat.S_IRUSR | stat.S_IXUSR)
    annotations = parse_kindle_export(str(FIXTURE))
    try:
        with pytest.raises(OSError):
            save_annotations(annotations[:1], str(target))
    finally:
        target.chmod(stat.S_IRWXU)


# --- parse_md_annotations_dir tool ---

MD_FIXTURES = Path(__file__).parent / "fixtures" / "annotations"


def test_parse_md_dir_returns_annotations() -> None:
    result = parse_md_annotations_dir(str(MD_FIXTURES))
    assert result["annotations"] != [] and len(result["annotations"]) == 4


def test_parse_md_dir_sorted_order() -> None:
    result = parse_md_annotations_dir(str(MD_FIXTURES))
    numbers = [a["number"] for a in result["annotations"]]
    assert numbers == sorted(numbers)


def test_parse_md_dir_annotation_fields() -> None:
    result = parse_md_annotations_dir(str(MD_FIXTURES))
    a = result["annotations"][0]
    assert a["book_title"] == "A Brief History of Time"
    assert a["author"] == "Stephen Hawking"
    assert "text" in a
    assert "chapter" in a
    assert "page" in a
    assert "location" in a
    assert "number" in a


def test_parse_md_dir_no_parse_errors() -> None:
    result = parse_md_annotations_dir(str(MD_FIXTURES))
    assert result["parse_errors"] == {}


def test_parse_md_dir_empty_directory(tmp_path: Path) -> None:
    result = parse_md_annotations_dir(str(tmp_path))
    assert result["annotations"] == []
    assert result["parse_errors"] == {}


def test_parse_md_dir_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        parse_md_annotations_dir("/tmp/no_such_dir_xyz")


def test_parse_md_dir_file_not_directory(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir.md"
    f.write_text("content", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        parse_md_annotations_dir(str(f))


def test_parse_md_dir_malformed_file_reported(tmp_path: Path) -> None:
    # Copy a valid fixture then add a malformed file
    for src in MD_FIXTURES.glob("*.md"):
        shutil.copy(src, tmp_path / src.name)
    bad = tmp_path / "000 - bad.md"
    bad.write_text("no frontmatter here", encoding="utf-8")
    result = parse_md_annotations_dir(str(tmp_path))
    assert len(result["annotations"]) == 4
    assert "000 - bad.md" in result["parse_errors"]


# --- generate_book_index prompt ---


def test_generate_book_index_returns_message() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    assert len(result) == 1
    assert result[0].role == "user"
    text = result[0].content.text
    assert "A Brief History of Time" in text
    assert "Stephen Hawking" in text


def test_generate_book_index_contains_annotations() -> None:
    result = generate_book_index(str(MD_FIXTURES))
    text = result[0].content.text
    # All 4 annotation titles should appear in the prompt
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


# --- anki_export tool ---


def test_anki_export_tool_returns_summary() -> None:
    with patch(
        "otb.mcp_server.export_annotations",
        return_value=ExportResult(created=4, skipped=0, failed=0),
    ):
        result = anki_export(str(MD_FIXTURES))
    assert result == {"created": 4, "skipped": 0, "failed": 0}


def test_anki_export_tool_missing_path() -> None:
    with pytest.raises(FileNotFoundError):
        anki_export("/tmp/no_such_dir_xyz_abc_mcp")


def test_anki_export_tool_file_not_directory(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir.md"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        anki_export(str(f))


def test_anki_export_tool_custom_deck() -> None:
    with patch(
        "otb.mcp_server.export_annotations",
        return_value=ExportResult(created=2, skipped=2, failed=0),
    ) as mock_exp:
        anki_export(str(MD_FIXTURES), deck="Books::Test")
    args = mock_exp.call_args
    assert args[1].get("deck") == "Books::Test" or args[0][1] == "Books::Test"


def test_anki_export_tool_anki_unreachable_raises() -> None:
    with patch(
        "otb.mcp_server.export_annotations",
        side_effect=AnkiConnectError("refused"),
    ):
        with pytest.raises(AnkiConnectError):
            anki_export(str(MD_FIXTURES))


# --- parse_zotero_export tool ---

ZOTERO_FIXTURES = Path(__file__).parent / "fixtures" / "zotero"


def test_parse_zotero_export_returns_annotations() -> None:
    result = parse_zotero_export(str(ZOTERO_FIXTURES))
    assert len(result) == 306


def test_parse_zotero_export_annotation_fields() -> None:
    result = parse_zotero_export(str(ZOTERO_FIXTURES))
    a = result[0]
    assert a["book_title"] == "Refactoring: Improving the Design of Existing Code"
    assert a["author"] == "Martin Fowler"
    assert a["page"] == "xi"
    assert a["location"] == 0
    assert a["color"] is None
    assert a["number"] == 1
    assert a["title"]  # non-empty


def test_parse_zotero_export_missing_directory() -> None:
    with pytest.raises(FileNotFoundError):
        parse_zotero_export("/tmp/no_such_zotero_dir_xyz")


def test_parse_zotero_export_file_not_directory(tmp_path: Path) -> None:
    f = tmp_path / "not_a_dir.md"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        parse_zotero_export(str(f))


# --- kindle_import_annotations prompt ---


def test_kindle_import_returns_messages() -> None:
    result = kindle_import_annotations(
        file_path="/tmp/exports/test.html"
    )
    assert len(result) >= 1
    assert result[0].role == "user"


def test_kindle_import_contains_tool_names() -> None:
    result = kindle_import_annotations(
        file_path="/tmp/exports/test.html"
    )
    text = result[0].content.text
    assert "parse_kindle_export" in text
    assert "save_annotations" in text
    assert "/tmp/exports/test.html" in text


def test_kindle_import_derives_notes_directory() -> None:
    result = kindle_import_annotations(
        file_path="/tmp/exports/test.html"
    )
    text = result[0].content.text
    assert "/tmp/exports/notes/" in text


def test_kindle_import_contains_title_instructions() -> None:
    result = kindle_import_annotations(
        file_path="/tmp/exports/test.html"
    )
    text = result[0].content.text
    assert "title" in text.lower()
    assert "10" in text

# pylint: disable=missing-function-docstring,too-many-arguments,too-many-positional-arguments
"""Tests for the markdown highlight writer."""
import stat
import sys
from pathlib import Path

import pytest

from otb.md_parser import parse_highlight_md
from otb.md_writer import write_highlight, write_highlights
from otb.parser import Book, Highlight


def _make_highlight(
    number: int = 1,
    title: str = "Test Title",
    text: str = "Some highlight text.",
    chapter: str = "Chapter One",
    page: int = 5,
    location: int = 100,
    color: str | None = "yellow",
) -> Highlight:
    return Highlight(
        book=Book(title="My Book", author="Jane Doe"),
        chapter=chapter,
        page=page,
        location=location,
        text=text,
        title=title,
        color=color,
        number=number,
    )


def test_filename_with_title(tmp_path: Path) -> None:
    h = _make_highlight(number=1, title="The Great Discovery")
    path = write_highlight(h, tmp_path)
    assert path.name == "001 - The Great Discovery.md"


def test_filename_without_title(tmp_path: Path) -> None:
    h = _make_highlight(number=3, title="")
    path = write_highlight(h, tmp_path)
    assert path.name == "003.md"


def test_frontmatter_fields_with_title(tmp_path: Path) -> None:
    h = _make_highlight(number=1, title="My Title")
    path = write_highlight(h, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert 'source: "My Book"' in content
    assert "author: Jane Doe" in content
    assert 'chapter: "Chapter One"' in content
    assert "page: 5" in content
    assert "location: 100" in content
    assert "type: highlight" in content
    assert "number: 1" in content


def test_body_with_title(tmp_path: Path) -> None:
    h = _make_highlight(title="My Title", text="Hello world.")
    path = write_highlight(h, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "# My Title\n" in content
    assert "> Hello world." in content


def test_body_without_title(tmp_path: Path) -> None:
    h = _make_highlight(title="", text="Hello world.")
    path = write_highlight(h, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "# " not in content
    assert "> Hello world." in content


def test_directory_created_automatically(tmp_path: Path) -> None:
    target = tmp_path / "new" / "subdir"
    assert not target.exists()
    write_highlight(_make_highlight(), target)
    assert target.exists()


def test_unique_filenames_via_number(tmp_path: Path) -> None:
    h1 = _make_highlight(number=1, text="Same text.")
    h2 = _make_highlight(number=2, text="Same text.", title="Same Title")
    p1 = write_highlight(h1, tmp_path)
    p2 = write_highlight(h2, tmp_path)
    assert p1 != p2


def test_round_trip_with_title(tmp_path: Path) -> None:
    h = _make_highlight(number=1, title="Round Trip Title", text="Some text here.")
    path = write_highlight(h, tmp_path)
    parsed = parse_highlight_md(path)
    assert parsed.title == "Round Trip Title"
    assert parsed.text == "Some text here."
    assert parsed.book.title == "My Book"
    assert parsed.book.author == "Jane Doe"
    assert parsed.chapter == "Chapter One"
    assert parsed.page == 5
    assert parsed.location == 100
    assert parsed.number == 1


def test_round_trip_without_title(tmp_path: Path) -> None:
    h = _make_highlight(number=2, title="", text="No title text.")
    path = write_highlight(h, tmp_path)
    parsed = parse_highlight_md(path)
    assert parsed.title == ""
    assert parsed.text == "No title text."


def test_write_highlights_returns_paths(tmp_path: Path) -> None:
    highlights = [_make_highlight(number=i, title=f"Title {i}") for i in range(1, 4)]
    paths = write_highlights(highlights, tmp_path)
    assert len(paths) == 3
    assert all(p.exists() for p in paths)


@pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
def test_non_writable_directory_raises(tmp_path: Path) -> None:
    target = tmp_path / "readonly"
    target.mkdir()
    target.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        with pytest.raises(OSError):
            write_highlights([_make_highlight()], target)
    finally:
        target.chmod(stat.S_IRWXU)


def test_filename_sanitisation(tmp_path: Path) -> None:
    h = _make_highlight(title='Hello: World / Test "quoted"')
    path = write_highlight(h, tmp_path)
    assert "/" not in path.name
    assert ":" not in path.name
    assert '"' not in path.name

# pylint: disable=missing-function-docstring,too-many-arguments,too-many-positional-arguments
"""Tests for the annotation markdown writer."""
import stat
import sys
from pathlib import Path

import pytest

from otb.md_parser import parse_annotation_md
from otb.md_writer import write_annotation, write_annotations, write_anki_id
from otb.parser import Annotation, Book


def _make_annotation(
    number: int = 1,
    title: str = "Test Title",
    text: str = "Some annotation text.",
    chapter: str = "Chapter One",
    page: str = "5",
    location: int = 100,
    color: str | None = "yellow",
) -> Annotation:
    return Annotation(
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
    a = _make_annotation(number=1, title="The Great Discovery")
    path = write_annotation(a, tmp_path)
    assert path.name == "001 - The Great Discovery.md"


def test_filename_without_title(tmp_path: Path) -> None:
    a = _make_annotation(number=3, title="")
    path = write_annotation(a, tmp_path)
    assert path.name == "003.md"


def test_frontmatter_fields_with_title(tmp_path: Path) -> None:
    a = _make_annotation(number=1, title="My Title")
    path = write_annotation(a, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert 'source: "My Book"' in content
    assert "author: Jane Doe" in content
    assert 'chapter: "Chapter One"' in content
    assert "page: 5" in content
    assert "location: 100" in content
    assert "type: annotation" in content
    assert "number: 1" in content


def test_body_with_title(tmp_path: Path) -> None:
    a = _make_annotation(title="My Title", text="Hello world.")
    path = write_annotation(a, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "# My Title\n" in content
    assert "> Hello world." in content


def test_body_without_title(tmp_path: Path) -> None:
    a = _make_annotation(title="", text="Hello world.")
    path = write_annotation(a, tmp_path)
    content = path.read_text(encoding="utf-8")
    assert "# " not in content
    assert "> Hello world." in content


def test_directory_created_automatically(tmp_path: Path) -> None:
    target = tmp_path / "new" / "subdir"
    assert not target.exists()
    write_annotation(_make_annotation(), target)
    assert target.exists()


def test_unique_filenames_via_number(tmp_path: Path) -> None:
    a1 = _make_annotation(number=1, text="Same text.")
    a2 = _make_annotation(number=2, text="Same text.", title="Same Title")
    p1 = write_annotation(a1, tmp_path)
    p2 = write_annotation(a2, tmp_path)
    assert p1 != p2


def test_round_trip_with_title(tmp_path: Path) -> None:
    a = _make_annotation(number=1, title="Round Trip Title", text="Some text here.")
    path = write_annotation(a, tmp_path)
    parsed = parse_annotation_md(path)
    assert parsed.title == "Round Trip Title"
    assert parsed.text == "Some text here."
    assert parsed.book.title == "My Book"
    assert parsed.book.author == "Jane Doe"
    assert parsed.chapter == "Chapter One"
    assert parsed.page == "5"
    assert parsed.location == 100
    assert parsed.number == 1


def test_round_trip_without_title(tmp_path: Path) -> None:
    a = _make_annotation(number=2, title="", text="No title text.")
    path = write_annotation(a, tmp_path)
    parsed = parse_annotation_md(path)
    assert parsed.title == ""
    assert parsed.text == "No title text."


def test_write_annotations_returns_paths(tmp_path: Path) -> None:
    annotations = [_make_annotation(number=i, title=f"Title {i}") for i in range(1, 4)]
    paths = write_annotations(annotations, tmp_path)
    assert len(paths) == 3
    assert all(p.exists() for p in paths)


@pytest.mark.skipif(sys.platform == "win32", reason="Unix permissions only")
def test_non_writable_directory_raises(tmp_path: Path) -> None:
    target = tmp_path / "readonly"
    target.mkdir()
    target.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        with pytest.raises(OSError):
            write_annotations([_make_annotation()], target)
    finally:
        target.chmod(stat.S_IRWXU)


def test_filename_sanitisation(tmp_path: Path) -> None:
    a = _make_annotation(title='Hello: World / Test "quoted"')
    path = write_annotation(a, tmp_path)
    assert "/" not in path.name
    assert ":" not in path.name
    assert '"' not in path.name


def test_write_anki_id_inserts_field(tmp_path: Path) -> None:
    path = write_annotation(_make_annotation(), tmp_path)
    write_anki_id(path, 1234567890)
    assert "anki_id: 1234567890" in path.read_text(encoding="utf-8")


def test_write_anki_id_field_in_frontmatter(tmp_path: Path) -> None:
    path = write_annotation(_make_annotation(), tmp_path)
    write_anki_id(path, 999)
    content = path.read_text(encoding="utf-8")
    # anki_id must appear between the --- delimiters
    frontmatter_end = content.index("---\n", 4)
    frontmatter = content[:frontmatter_end]
    assert "anki_id: 999" in frontmatter


def test_write_anki_id_updates_existing(tmp_path: Path) -> None:
    path = write_annotation(_make_annotation(), tmp_path)
    write_anki_id(path, 1111)
    write_anki_id(path, 2222)
    content = path.read_text(encoding="utf-8")
    assert "anki_id: 2222" in content
    assert "anki_id: 1111" not in content


def test_write_anki_id_preserves_other_fields(tmp_path: Path) -> None:
    path = write_annotation(_make_annotation(page="7", location=77), tmp_path)
    write_anki_id(path, 42)
    parsed = parse_annotation_md(path)
    assert parsed.page == "7"
    assert parsed.location == 77
    assert parsed.anki_id == 42

"""Tests for the Boox annotation parser."""
# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest

from otb.parser import Annotation, Book
from otb.boox_parser import parse_boox_annotations
from otb.zotero_parser import parse_book_metadata

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "boox"


# ---------------------------------------------------------------------------
# T003: parse_book_metadata (reused from zotero_parser)
# ---------------------------------------------------------------------------


def test_parse_book_metadata() -> None:
    book = parse_book_metadata(FIXTURE_DIR / "book.txt")
    assert book == Book(
        title="Just for Fun: The Story of an Accidental Revolutionary",
        author="Linus Torvalds & David Diamond",
    )


# ---------------------------------------------------------------------------
# T004: annotation count from fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def annotations() -> list[Annotation]:
    result, _figure_map = parse_boox_annotations(FIXTURE_DIR)
    return result


def test_annotation_count(annotations: list[Annotation]) -> None:
    assert len(annotations) == 35


# ---------------------------------------------------------------------------
# T005: first annotation field values
# ---------------------------------------------------------------------------


def test_first_annotation_fields(annotations: list[Annotation]) -> None:
    a = annotations[0]
    assert a.book == Book(
        title="Just for Fun: The Story of an Accidental Revolutionary",
        author="Linus Torvalds & David Diamond",
    )
    assert a.chapter == "Preface: The Meaning of Life I (Sex, War, Linux)"
    assert a.page == ""
    assert a.location == 17
    assert a.text.startswith("L: I\u2019ll give you a few examples")
    assert a.title  # non-empty auto-generated title
    assert a.color is None


# ---------------------------------------------------------------------------
# T006: chapter tracking
# ---------------------------------------------------------------------------


def test_chapter_tracking(annotations: list[Annotation]) -> None:
    # First two annotations are in the Preface
    assert annotations[0].chapter == (
        "Preface: The Meaning of Life I (Sex, War, Linux)"
    )
    assert annotations[1].chapter == (
        "Preface: The Meaning of Life I (Sex, War, Linux)"
    )
    # Third annotation is in chapter "I"
    assert annotations[2].chapter == "I"
    # Fourth annotation is in chapter "III"
    assert annotations[3].chapter == "III"
    # The "V: The Beauty of Programming" chapter
    assert annotations[8].chapter == "V: The Beauty of Programming"


# ---------------------------------------------------------------------------
# T007: multi-line annotation text
# ---------------------------------------------------------------------------


def test_multiline_annotation(annotations: list[Annotation]) -> None:
    # Annotation at index 8 (page 114, V: The Beauty of Programming)
    # spans multiple lines in the export
    a = annotations[8]
    assert "V: The Beauty of Programming" in a.text
    assert "And yet, to the outside" in a.text


# ---------------------------------------------------------------------------
# T008: missing files raise FileNotFoundError
# ---------------------------------------------------------------------------


def test_missing_book_txt(tmp_path: Path) -> None:
    ann = tmp_path / "annotations.txt"
    ann.write_text("Reading Notes | <<Test>>Author\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        parse_boox_annotations(tmp_path)


def test_missing_annotation_file(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text("Title \nTest Book\nAuthors \nTest Author\n",
                    encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        parse_boox_annotations(tmp_path)


# ---------------------------------------------------------------------------
# T009: empty annotation blocks are skipped
# ---------------------------------------------------------------------------


def test_empty_annotation_skipped(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text("Title \nTest Book\nAuthors \nTest Author\n",
                    encoding="utf-8")
    ann = tmp_path / "annotations.txt"
    ann.write_text(
        "Reading Notes | <<Test>>Author\n"
        "2026-01-01 10:00  |  Page No.: 1\n"
        "-------------------\n"
        "2026-01-01 10:01  |  Page No.: 2\n"
        "Some actual text here.\n"
        "-------------------\n",
        encoding="utf-8",
    )
    result, _ = parse_boox_annotations(tmp_path)
    assert len(result) == 1
    assert result[0].text == "Some actual text here."


# ---------------------------------------------------------------------------
# T013: sequential numbering
# ---------------------------------------------------------------------------


def test_sequential_numbering(annotations: list[Annotation]) -> None:
    assert [a.number for a in annotations] == list(
        range(1, len(annotations) + 1)
    )

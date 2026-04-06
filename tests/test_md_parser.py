"""Tests for the annotation markdown parser."""
# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest

from otb.parser import Annotation, Book
from otb.md_parser import parse_annotation_md, parse_annotation_dir

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "annotations"


@pytest.fixture
def annotations() -> list[Annotation]:
    return parse_annotation_dir(FIXTURES_DIR)


def test_count(annotations: list[Annotation]) -> None:
    assert len(annotations) == 4


def test_book_metadata(annotations: list[Annotation]) -> None:
    for a in annotations:
        assert a.book == Book(title="A Brief History of Time", author="Stephen Hawking")


def test_chapter_assignment(annotations: list[Annotation]) -> None:
    assert annotations[0].chapter == "1   Our Picture of the Universe"
    assert annotations[2].chapter == "2   Space and Time"


def test_page_and_location(annotations: list[Annotation]) -> None:
    assert annotations[0].page == 1
    assert annotations[0].location == 42
    assert annotations[2].page == 22
    assert annotations[2].location == 310


def test_no_color(annotations: list[Annotation]) -> None:
    for a in annotations:
        assert a.color is None


def test_text(annotations: list[Annotation]) -> None:
    assert annotations[0].text == "A well-known scientist once gave a public lecture on astronomy."
    assert "provisional" in annotations[1].text


def test_title(annotations: list[Annotation]) -> None:
    assert annotations[0].title == "A Well-Known Scientist Once Gave a Public Lecture on Astronomy"


def test_numbers(annotations: list[Annotation]) -> None:
    assert [a.number for a in annotations] == [1, 2, 3, 4]


def test_single_file() -> None:
    path = FIXTURES_DIR / "001 - A Well-Known Scientist Once Gave a Public Lecture on Astronomy.md"
    a = parse_annotation_md(path)
    assert a.page == 1
    assert a.location == 42
    assert a.book.author == "Stephen Hawking"

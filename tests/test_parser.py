"""Tests for the notebook HTML parser."""
# pylint: disable=missing-function-docstring
from pathlib import Path

import pytest

from otb.parser import Annotation, Book, parse_notebook

FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"


@pytest.fixture
def annotations() -> list[Annotation]:
    return parse_notebook(FIXTURE)


def test_count(annotations: list[Annotation]) -> None:
    assert len(annotations) == 4


def test_book_metadata(annotations: list[Annotation]) -> None:
    for a in annotations:
        assert a.book == Book(title="A Brief History of Time", author="Stephen Hawking")


def test_chapter_assignment(annotations: list[Annotation]) -> None:
    assert annotations[0].chapter == "1   Our Picture of the Universe"
    assert annotations[1].chapter == "1   Our Picture of the Universe"
    assert annotations[2].chapter == "2   Space and Time"
    assert annotations[3].chapter == "2   Space and Time"


def test_page_and_location(annotations: list[Annotation]) -> None:
    assert annotations[0].page == 1
    assert annotations[0].location == 42
    assert annotations[2].page == 22
    assert annotations[2].location == 310


def test_annotation_colors(annotations: list[Annotation]) -> None:
    assert annotations[0].color == "yellow"
    assert annotations[1].color == "blue"
    assert annotations[3].color == "pink"


def test_text(annotations: list[Annotation]) -> None:
    assert annotations[0].text == "A well-known scientist once gave a public lecture on astronomy."
    assert "provisional" in annotations[1].text


def test_title(annotations: list[Annotation]) -> None:
    assert annotations[0].title == "A Well-Known Scientist Once Gave A Public"
    assert annotations[2].title == "The Theory Of Relativity Put An End"


def test_numbers(annotations: list[Annotation]) -> None:
    assert [a.number for a in annotations] == [1, 2, 3, 4]


def test_generate_title_false() -> None:
    results = parse_notebook(FIXTURE, generate_title=False)
    assert all(a.title == "" for a in results)

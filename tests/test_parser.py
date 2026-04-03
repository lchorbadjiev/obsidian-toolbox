"""Tests for the notebook HTML parser."""
from pathlib import Path

import pytest

from otb.parser import Book, Highlight, parse_notebook

FIXTURE = Path(__file__).parent / "fixtures" / "A Brief History of Time - Notebook.html"


@pytest.fixture
def highlights() -> list[Highlight]:
    return parse_notebook(FIXTURE)


def test_count(highlights: list[Highlight]) -> None:
    assert len(highlights) == 4


def test_book_metadata(highlights: list[Highlight]) -> None:
    for h in highlights:
        assert h.book == Book(title="A Brief History of Time", author="Stephen Hawking")


def test_chapter_assignment(highlights: list[Highlight]) -> None:
    assert highlights[0].chapter == "1   Our Picture of the Universe"
    assert highlights[1].chapter == "1   Our Picture of the Universe"
    assert highlights[2].chapter == "2   Space and Time"
    assert highlights[3].chapter == "2   Space and Time"


def test_page_and_location(highlights: list[Highlight]) -> None:
    assert highlights[0].page == 1
    assert highlights[0].location == 42
    assert highlights[2].page == 22
    assert highlights[2].location == 310


def test_highlight_colors(highlights: list[Highlight]) -> None:
    assert highlights[0].color == "yellow"
    assert highlights[1].color == "blue"
    assert highlights[3].color == "pink"


def test_text(highlights: list[Highlight]) -> None:
    assert highlights[0].text == "A well-known scientist once gave a public lecture on astronomy."
    assert "provisional" in highlights[1].text

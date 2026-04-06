"""Tests for the Zotero annotation parser."""
# pylint: disable=missing-function-docstring
from pathlib import Path
from unittest.mock import patch

import pytest

from otb.parser import Annotation, Book
from otb.zotero_parser import parse_book_metadata, parse_zotero_annotations

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "zotero"


# ---------------------------------------------------------------------------
# T002: parse_book_metadata
# ---------------------------------------------------------------------------


def test_parse_book_metadata() -> None:
    book = parse_book_metadata(FIXTURE_DIR / "book.txt")
    assert book == Book(
        title="Refactoring: Improving the Design of Existing Code",
        author="Martin Fowler",
    )


def test_parse_book_metadata_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        parse_book_metadata(tmp_path / "nonexistent.txt")


# ---------------------------------------------------------------------------
# T004: empty Annotations.md
# ---------------------------------------------------------------------------


def test_empty_annotations(tmp_path: Path) -> None:
    book_txt = tmp_path / "book.txt"
    book_txt.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n", encoding="utf-8"
    )
    ann_md = tmp_path / "Annotations.md"
    ann_md.write_text("# Annotations\n(date)\n", encoding="utf-8")
    assert not parse_zotero_annotations(tmp_path)


# ---------------------------------------------------------------------------
# T005: annotation count from fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def annotations() -> list[Annotation]:
    return parse_zotero_annotations(FIXTURE_DIR)


def test_annotation_count(annotations: list[Annotation]) -> None:
    assert len(annotations) == 306


# ---------------------------------------------------------------------------
# T006: annotation field values
# ---------------------------------------------------------------------------


def test_first_annotation_fields(annotations: list[Annotation]) -> None:
    a = annotations[0]
    assert a.page == 11  # roman numeral xi -> 11
    assert a.location == 11
    assert a.text.startswith("So, what\u2019s the problem?")
    assert a.title == "So, What\u2019S The Problem"
    assert a.number == 1
    assert a.chapter == ""
    assert a.color is None
    assert a.book == Book(
        title="Refactoring: Improving the Design of Existing Code",
        author="Martin Fowler",
    )


# ---------------------------------------------------------------------------
# T007: sequential numbering
# ---------------------------------------------------------------------------


def test_sequential_numbering(annotations: list[Annotation]) -> None:
    assert [a.number for a in annotations] == list(range(1, len(annotations) + 1))


# ---------------------------------------------------------------------------
# T008: missing book.txt raises FileNotFoundError
# ---------------------------------------------------------------------------


def test_missing_book_txt(tmp_path: Path) -> None:
    ann_md = tmp_path / "Annotations.md"
    ann_md.write_text("# Annotations\n(date)\n", encoding="utf-8")
    with pytest.raises(FileNotFoundError):
        parse_zotero_annotations(tmp_path)


# ---------------------------------------------------------------------------
# T015: single-word annotation
# ---------------------------------------------------------------------------


def _make_zotero_dir(tmp_path: Path, annotation_lines: str) -> Path:
    """Helper to create a temp Zotero export directory."""
    book_txt = tmp_path / "book.txt"
    book_txt.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n", encoding="utf-8"
    )
    ann_md = tmp_path / "Annotations.md"
    ann_md.write_text(
        f"# Annotations\n(date)\n\n{annotation_lines}\n", encoding="utf-8"
    )
    return tmp_path


def test_single_word_annotation(tmp_path: Path) -> None:
    d = _make_zotero_dir(tmp_path, "\u201cIf\u201d (\u201cBook\u201d, p. 4)")
    result = parse_zotero_annotations(d)
    assert len(result) == 1
    assert result[0].text == "If"
    assert result[0].title  # non-empty title


# ---------------------------------------------------------------------------
# T016: short fragment annotation
# ---------------------------------------------------------------------------


def test_short_fragment_annotation(tmp_path: Path) -> None:
    d = _make_zotero_dir(
        tmp_path, "\u201cyour design\u201d (\u201cBook\u201d, p. 12)"
    )
    result = parse_zotero_annotations(d)
    assert len(result) == 1
    assert result[0].text == "your design"
    assert result[0].page == 12


# ---------------------------------------------------------------------------
# T017: unparseable line is skipped
# ---------------------------------------------------------------------------


def test_unparseable_line_skipped(tmp_path: Path) -> None:
    lines = (
        "\u201cGood text\u201d (\u201cBook\u201d, p. 1)\n"
        "Some random line without page reference\n"
        "\u201cMore text\u201d (\u201cBook\u201d, p. 2)"
    )
    d = _make_zotero_dir(tmp_path, lines)
    result = parse_zotero_annotations(d)
    assert len(result) == 2
    assert result[0].text == "Good text"
    assert result[1].text == "More text"


# ---------------------------------------------------------------------------
# T010: word splitting in parsed output
# ---------------------------------------------------------------------------


def test_word_splitting_applied(annotations: list[Annotation]) -> None:
    # Annotation 67 (0-indexed) originally has "SoftwareWithout"
    texts = [a.text for a in annotations]
    joined = " ".join(texts)
    assert "SoftwareWithout" not in joined
    assert "Software Without" in joined


# ---------------------------------------------------------------------------
# T011: annotation count preserved after splitting
# ---------------------------------------------------------------------------


def test_annotation_count_with_splitting(annotations: list[Annotation]) -> None:
    assert len(annotations) == 306


# ---------------------------------------------------------------------------
# T012: fix count summary on stderr
# ---------------------------------------------------------------------------


def test_fix_count_summary(capfd: pytest.CaptureFixture[str]) -> None:
    parse_zotero_annotations(FIXTURE_DIR)
    captured = capfd.readouterr()
    assert "Fixed" in captured.err


# ---------------------------------------------------------------------------
# T013: aspell not found raises RuntimeError
# ---------------------------------------------------------------------------


def test_aspell_not_found_raises() -> None:
    with patch("otb.word_fixer.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="aspell"):
            parse_zotero_annotations(FIXTURE_DIR)

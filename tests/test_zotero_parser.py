"""Tests for the Zotero annotation parser."""
# pylint: disable=missing-function-docstring,import-outside-toplevel
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
    result, _ = parse_zotero_annotations(tmp_path)
    assert not result


# ---------------------------------------------------------------------------
# T005: annotation count from fixture
# ---------------------------------------------------------------------------


@pytest.fixture
def annotations() -> list[Annotation]:
    result, _ = parse_zotero_annotations(FIXTURE_DIR)
    return result


def test_annotation_count(annotations: list[Annotation]) -> None:
    assert len(annotations) == 306


# ---------------------------------------------------------------------------
# T006: annotation field values
# ---------------------------------------------------------------------------


def test_first_annotation_fields(annotations: list[Annotation]) -> None:
    a = annotations[0]
    assert a.page == "xi"
    assert a.location == 0
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
    result, _ = parse_zotero_annotations(d)
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
    result, _ = parse_zotero_annotations(d)
    assert len(result) == 1
    assert result[0].text == "your design"
    assert result[0].page == "12"


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
    result, _ = parse_zotero_annotations(d)
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


# ---------------------------------------------------------------------------
# HTML parser tests
# ---------------------------------------------------------------------------

HTML_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "zotero-html"


def test_parse_html_annotation_count() -> None:
    annotations, _ = parse_zotero_annotations(HTML_FIXTURE_DIR)
    assert len(annotations) > 100  # reasonable count


def test_parse_html_first_annotation() -> None:
    annotations, _ = parse_zotero_annotations(HTML_FIXTURE_DIR)
    a = annotations[0]
    assert "bit rot" in a.text
    assert a.page == "14"
    assert a.color == "#ffd400"


def test_parse_html_color_variety() -> None:
    annotations, _ = parse_zotero_annotations(HTML_FIXTURE_DIR)
    colors = {a.color for a in annotations if a.color}
    assert len(colors) >= 3


def test_parse_html_color_stripped_alpha() -> None:
    annotations, _ = parse_zotero_annotations(HTML_FIXTURE_DIR)
    for a in annotations:
        if a.color:
            assert len(a.color) == 7  # "#XXXXXX"
            assert a.color.startswith("#")


def test_parse_html_with_word_fixing() -> None:
    annotations, _ = parse_zotero_annotations(HTML_FIXTURE_DIR)
    all_text = " ".join(a.text for a in annotations)
    # Word fixer should fix concatenated words
    assert "softwareentropy" not in all_text.lower()


def test_fallback_to_markdown(tmp_path: Path) -> None:
    """Only Annotations.md present → uses markdown parser."""
    import shutil
    shutil.copy(FIXTURE_DIR / "book.txt", tmp_path / "book.txt")
    shutil.copy(
        FIXTURE_DIR / "Annotations.md", tmp_path / "Annotations.md"
    )
    annotations, _ = parse_zotero_annotations(tmp_path)
    assert len(annotations) == 306
    assert all(a.color is None for a in annotations)


def test_prefer_html_over_markdown(tmp_path: Path) -> None:
    """Both files present → uses HTML (has colors)."""
    import shutil
    shutil.copy(
        HTML_FIXTURE_DIR / "book.txt", tmp_path / "book.txt"
    )
    shutil.copy(
        HTML_FIXTURE_DIR / "Annotations.html",
        tmp_path / "Annotations.html",
    )
    # Also copy a dummy markdown so both exist
    (tmp_path / "Annotations.md").write_text(
        "# Annotations\n", encoding="utf-8"
    )
    annotations, _ = parse_zotero_annotations(tmp_path)
    # Should have colors (HTML was used)
    assert any(a.color is not None for a in annotations)

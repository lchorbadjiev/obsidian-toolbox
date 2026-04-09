"""Tests for EPUB figure extraction."""
# pylint: disable=missing-function-docstring,import-outside-toplevel
import shutil
from pathlib import Path

from otb.boox_parser import parse_boox_annotations
from otb.epub_figures import detect_figure_refs, parse_epub_figures
from otb.md_writer import write_annotation
from otb.mcp_server import parse_boox_export
from otb.parser import Annotation, Book, FigureRef

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "boox"
TEST_EPUB = FIXTURE_DIR / "test.epub"


# ---------------------------------------------------------------------------
# T003: parse_epub_figures returns figure map from test EPUB
# ---------------------------------------------------------------------------


def test_parse_epub_figures() -> None:
    result = parse_epub_figures(TEST_EPUB)
    assert "1.1" in result
    assert "1.2" in result
    # Each entry is (bytes, extension)
    img_bytes, ext = result["1.1"]
    assert len(img_bytes) > 0
    assert ext in (".jpg", ".jpeg")


# ---------------------------------------------------------------------------
# T004: parse_epub_figures on missing path returns empty dict
# ---------------------------------------------------------------------------


def test_parse_epub_figures_missing() -> None:
    result = parse_epub_figures(Path("/tmp/nonexistent.epub"))
    assert not result


# ---------------------------------------------------------------------------
# T005: detect_figure_refs caption pattern
# ---------------------------------------------------------------------------


def test_detect_figure_refs_caption() -> None:
    text = (
        "FIGURE 2.1. Per capita GDP, 1000\u20132008. "
        "Note: In 1990 dollars."
    )
    assert detect_figure_refs(text) == ["2.1"]


# ---------------------------------------------------------------------------
# T006: detect_figure_refs inline pattern
# ---------------------------------------------------------------------------


def test_detect_figure_refs_inline() -> None:
    text = (
        "Yet until the beginning of the nineteenth century, "
        "the rural population made up approximately 90 percent "
        "of the total population in Europe (Figure 2.3).3"
    )
    assert detect_figure_refs(text) == ["2.3"]


# ---------------------------------------------------------------------------
# T007: detect_figure_refs multiple inline references
# ---------------------------------------------------------------------------


def test_detect_figure_refs_multiple() -> None:
    text = (
        "Results show impact (Figure 3.5). It is noteworthy "
        "that this effect was positive (Figure 4.7)."
    )
    assert detect_figure_refs(text) == ["3.5", "4.7"]


# ---------------------------------------------------------------------------
# T008: detect_figure_refs no references
# ---------------------------------------------------------------------------


def test_detect_figure_refs_none() -> None:
    text = "This is a plain annotation with no figure mentions."
    assert not detect_figure_refs(text)


# ---------------------------------------------------------------------------
# T013: boox parse with EPUB attaches figures
# ---------------------------------------------------------------------------


def test_boox_parse_with_epub(tmp_path: Path) -> None:
    # Setup temp dir with book.txt, annotation file, and EPUB
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "annotations.txt"
    ann.write_text(
        "Reading Notes | <<Test>>Author\n"
        "2026-01-01 10:00  |  Page No.: 1\n"
        "FIGURE 1.1. Test figure one caption.\n"
        "-------------------\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_EPUB, tmp_path / "test.epub")

    annotations, _figure_map = parse_boox_annotations(tmp_path)
    assert len(annotations) == 1
    assert len(annotations[0].figures) == 1
    assert annotations[0].figures[0].label == "1.1"


# ---------------------------------------------------------------------------
# T014: write_annotation with figure embeds image link
# ---------------------------------------------------------------------------


def test_write_annotation_with_figure(tmp_path: Path) -> None:
    figure_data = {
        "1.1": (b"\xff\xd8\xff\xe0" + b"\x00" * 20, ".jpg"),
    }
    a = Annotation(
        book=Book(title="Test", author="Author"),
        chapter="Ch1",
        page="",
        location=1,
        text="FIGURE 1.1. Test caption.",
        title="Figure 1.1",
        figures=[FigureRef(label="1.1")],
        number=1,
    )
    path = write_annotation(a, tmp_path, figure_data=figure_data)
    content = path.read_text(encoding="utf-8")
    assert "![Figure 1.1](images/figure-1-1.jpg)" in content
    img_path = tmp_path / "images" / "figure-1-1.jpg"
    assert img_path.exists()


# ---------------------------------------------------------------------------
# T020: inline figure reference detected in boox parse
# ---------------------------------------------------------------------------


def test_boox_parse_inline_figure_ref(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "annotations.txt"
    ann.write_text(
        "Reading Notes | <<Test>>Author\n"
        "2026-01-01 10:00  |  Page No.: 1\n"
        "Population in Europe (Figure 1.1).3 This share.\n"
        "-------------------\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_EPUB, tmp_path / "test.epub")

    annotations, _figure_map = parse_boox_annotations(tmp_path)
    assert len(annotations) == 1
    assert len(annotations[0].figures) == 1
    assert annotations[0].figures[0].label == "1.1"


# ---------------------------------------------------------------------------
# T021: multiple inline figure references
# ---------------------------------------------------------------------------


def test_boox_parse_multiple_inline_refs(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "annotations.txt"
    ann.write_text(
        "Reading Notes | <<Test>>Author\n"
        "2026-01-01 10:00  |  Page No.: 1\n"
        "See Figure 1.1 and Figure 1.2 for details.\n"
        "-------------------\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_EPUB, tmp_path / "test.epub")

    annotations, _figure_map = parse_boox_annotations(tmp_path)
    assert len(annotations) == 1
    assert len(annotations[0].figures) == 2
    labels = [f.label for f in annotations[0].figures]
    assert "1.1" in labels
    assert "1.2" in labels


# ---------------------------------------------------------------------------
# T024: no EPUB → empty figures, no errors
# ---------------------------------------------------------------------------


def test_boox_parse_no_epub_unchanged(tmp_path: Path) -> None:
    # Copy only book.txt and annotations.txt (no EPUB) to temp dir
    shutil.copy(FIXTURE_DIR / "book.txt", tmp_path / "book.txt")
    shutil.copy(
        FIXTURE_DIR / "annotations.txt",
        tmp_path / "annotations.txt",
    )

    annotations, figure_map = parse_boox_annotations(tmp_path)
    assert len(annotations) == 35
    assert not figure_map
    for a in annotations:
        assert a.figures == []


# ---------------------------------------------------------------------------
# T027: MCP tool includes figures field
# ---------------------------------------------------------------------------


def test_parse_boox_export_figures(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "annotations.txt"
    ann.write_text(
        "Reading Notes | <<Test>>Author\n"
        "2026-01-01 10:00  |  Page No.: 1\n"
        "FIGURE 1.1. Test caption.\n"
        "-------------------\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_EPUB, tmp_path / "test.epub")

    import json as _json

    result = parse_boox_export(str(tmp_path))
    assert result["count"] == 1
    assert result["figures_dir"] is not None
    # Verify annotations in temp file have figures
    with open(result["file_path"], encoding="utf-8") as f:
        annotations = _json.load(f)
    assert len(annotations[0]["figures"]) == 1
    assert annotations[0]["figures"][0]["label"] == "1.1"

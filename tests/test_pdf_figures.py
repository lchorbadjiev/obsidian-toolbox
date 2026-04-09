"""Tests for PDF figure extraction."""
# pylint: disable=missing-function-docstring,import-outside-toplevel
import json
import shutil
from pathlib import Path

from click.testing import CliRunner

from otb.cli import main
from otb.mcp_server import parse_zotero_export
from otb.pdf_figures import detect_zotero_figure_refs, extract_page_image
from otb.zotero_parser import parse_zotero_annotations

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "zotero"
TEST_PDF = FIXTURE_DIR / "test.pdf"


# ---------------------------------------------------------------------------
# T003: extract_page_image returns image data
# ---------------------------------------------------------------------------


def test_extract_page_image() -> None:
    result = extract_page_image(TEST_PDF, 0)
    assert result is not None
    img_bytes, ext = result
    assert len(img_bytes) > 0
    assert ext in (".jpg", ".jpeg")


# ---------------------------------------------------------------------------
# T004: extract_page_image no images returns None
# ---------------------------------------------------------------------------


def test_extract_page_image_no_images(tmp_path: Path) -> None:
    # Create a minimal PDF with no images using pypdf
    from pypdf import PdfWriter  # noqa: PLC0415

    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    pdf_path = tmp_path / "blank.pdf"
    with open(pdf_path, "wb") as f:
        writer.write(f)
    assert extract_page_image(pdf_path, 0) is None


# ---------------------------------------------------------------------------
# T005: extract_page_image missing PDF returns None
# ---------------------------------------------------------------------------


def test_extract_page_image_missing_pdf() -> None:
    result = extract_page_image(Path("/tmp/nonexistent.pdf"), 0)
    assert result is None


# ---------------------------------------------------------------------------
# T006: detect caption pattern
# ---------------------------------------------------------------------------


def test_detect_zotero_figure_refs_caption() -> None:
    text = "Figure 5-2. Monolithic architectures always have a quantum"
    refs = detect_zotero_figure_refs(text, "107")
    assert refs == [("5-2", "107")]


# ---------------------------------------------------------------------------
# T007: detect inline pattern
# ---------------------------------------------------------------------------


def test_detect_zotero_figure_refs_inline() -> None:
    text = "as illustrated in Figure 2-1"
    refs = detect_zotero_figure_refs(text, "26")
    assert refs == [("2-1", "26")]


# ---------------------------------------------------------------------------
# T008: detect "Get the figure" request
# ---------------------------------------------------------------------------


def test_detect_zotero_figure_refs_request() -> None:
    text = "Get the figure 5-17"
    refs = detect_zotero_figure_refs(text, "128")
    assert refs == [("5-17", "128")]


# ---------------------------------------------------------------------------
# T009: no figure references
# ---------------------------------------------------------------------------


def test_detect_zotero_figure_refs_none() -> None:
    text = "This is a plain annotation with no figure mentions."
    refs = detect_zotero_figure_refs(text, "42")
    assert not refs


# ---------------------------------------------------------------------------
# T015: zotero parse with PDF attaches figures
# ---------------------------------------------------------------------------


def test_zotero_parse_with_pdf_caption(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "Annotations.md"
    ann.write_text(
        "# Annotations\n(date)\n\n"
        "\u201cFigure 1-1. Test figure caption.\u201d"
        " (\u201cTest Book\u201d, p. 1)\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_PDF, tmp_path / "test.pdf")

    annotations, figure_map = parse_zotero_annotations(tmp_path)
    assert len(annotations) == 1
    assert len(annotations[0].figures) == 1
    assert annotations[0].figures[0].label == "1-1"
    assert "1-1" in figure_map


# ---------------------------------------------------------------------------
# T016: CLI with PDF writes images
# ---------------------------------------------------------------------------


def test_zotero_cli_with_pdf_writes_images(tmp_path: Path) -> None:
    src = tmp_path / "input"
    src.mkdir()
    book = src / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = src / "Annotations.md"
    ann.write_text(
        "# Annotations\n(date)\n\n"
        "\u201cFigure 1-1. Test figure caption.\u201d"
        " (\u201cTest Book\u201d, p. 1)\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_PDF, src / "test.pdf")

    out = tmp_path / "output"
    result = CliRunner().invoke(
        main, ["zotero", "parse", str(src), str(out)]
    )
    assert result.exit_code == 0
    assert (out / "images").is_dir()
    images = list((out / "images").glob("*"))
    assert len(images) >= 1
    # Verify markdown contains image link
    md_files = list(out.glob("*.md"))
    assert len(md_files) == 1
    content = md_files[0].read_text(encoding="utf-8")
    assert "![Figure 1-1]" in content


# ---------------------------------------------------------------------------
# T022: inline figure reference detected
# ---------------------------------------------------------------------------


def test_zotero_parse_inline_figure_ref(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "Annotations.md"
    ann.write_text(
        "# Annotations\n(date)\n\n"
        "\u201cas illustrated in Figure 1-1\u201d"
        " (\u201cTest Book\u201d, p. 1)\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_PDF, tmp_path / "test.pdf")

    annotations, _fig_map = parse_zotero_annotations(tmp_path)
    assert len(annotations) == 1
    assert len(annotations[0].figures) == 1
    assert annotations[0].figures[0].label == "1-1"


# ---------------------------------------------------------------------------
# T024: no PDF → empty figures, no errors
# ---------------------------------------------------------------------------


def test_zotero_parse_no_pdf_unchanged(tmp_path: Path) -> None:
    # Copy only book.txt and Annotations.md (no PDF)
    shutil.copy(FIXTURE_DIR / "book.txt", tmp_path / "book.txt")
    shutil.copy(
        FIXTURE_DIR / "Annotations.md",
        tmp_path / "Annotations.md",
    )

    annotations, figure_map = parse_zotero_annotations(tmp_path)
    assert len(annotations) == 306
    assert not figure_map
    for a in annotations:
        assert a.figures == []


# ---------------------------------------------------------------------------
# MCP tool returns summary with figures_dir
# ---------------------------------------------------------------------------


def test_parse_zotero_export_with_pdf(tmp_path: Path) -> None:
    book = tmp_path / "book.txt"
    book.write_text(
        "Title \nTest Book\nAuthors \nTest Author\n",
        encoding="utf-8",
    )
    ann = tmp_path / "Annotations.md"
    ann.write_text(
        "# Annotations\n(date)\n\n"
        "\u201cFigure 1-1. Test caption.\u201d"
        " (\u201cTest Book\u201d, p. 1)\n",
        encoding="utf-8",
    )
    shutil.copy(TEST_PDF, tmp_path / "test.pdf")

    result = parse_zotero_export(str(tmp_path))
    assert result["count"] == 1
    assert result["figures_dir"] is not None
    with open(result["file_path"], encoding="utf-8") as f:
        annotations = json.load(f)
    assert len(annotations[0]["figures"]) == 1

"""Writer for annotation markdown files."""
import re
from pathlib import Path

from otb.epub_figures import FigureMap
from otb.parser import Annotation

_ANKI_ID_RE = re.compile(r"^anki_id:.*$", re.MULTILINE)

_UNSAFE_RE = re.compile(r'[/\\:*?"<>|]')
_FILENAME_MAX = 60


def _sanitize(title: str) -> str:
    """Replace filename-unsafe characters and truncate."""
    sanitized = _UNSAFE_RE.sub("-", title)
    return sanitized[:_FILENAME_MAX]


def _render(a: Annotation) -> str:
    """Render an Annotation as a markdown string."""
    lines = [
        "---",
        f'source: "{a.book.title}"',
        f"author: {a.book.author}",
        f'chapter: "{a.chapter}"',
        f"page: {a.page}",
        f"location: {a.location}",
        "type: annotation",
        f"number: {a.number}",
        "---",
        "",
    ]
    if a.title:
        lines.append(f"# {a.title}")
        lines.append("")
    lines.append(f"> {a.text}")
    lines.append("")
    return "\n".join(lines)


def write_annotation(
    a: Annotation,
    directory: Path,
    figure_data: FigureMap | None = None,
) -> Path:
    """Write a single annotation to a markdown file in directory.

    If figure_data is provided and the annotation has figures, the
    corresponding images are extracted to an images/ subdirectory
    and image links are appended to the markdown.

    The directory is created if it does not exist. Returns the path written.
    """
    directory.mkdir(parents=True, exist_ok=True)
    if a.title:
        filename = f"{a.number:03d} - {_sanitize(a.title)}.md"
    else:
        filename = f"{a.number:03d}.md"
    path = directory / filename
    content = _render(a)

    # Write figure images (if data provided) and append links
    if a.figures:
        img_lines: list[str] = []
        if figure_data:
            img_dir = directory / "images"
            img_dir.mkdir(exist_ok=True)
        for fig in a.figures:
            if figure_data and fig.label in figure_data:
                img_bytes, ext = figure_data[fig.label]
                normalized = f"figure-{fig.label.replace('.', '-')}{ext}"
                (img_dir / normalized).write_bytes(img_bytes)
                fig.image_path = f"images/{normalized}"
            if fig.image_path:
                img_lines.append(
                    f"![Figure {fig.label}]({fig.image_path})"
                )
            else:
                normalized = f"figure-{fig.label.replace('.', '-')}.jpg"
                img_lines.append(
                    f"![Figure {fig.label}](images/{normalized})"
                )
        if img_lines:
            content += "\n".join(img_lines) + "\n"

    path.write_text(content, encoding="utf-8")
    return path


def write_anki_id(path: Path, anki_id: int) -> None:
    """Insert or replace the anki_id field in an annotation file's frontmatter.

    Raises OSError if the file cannot be written.
    """
    content = path.read_text(encoding="utf-8")
    new_line = f"anki_id: {anki_id}"
    if _ANKI_ID_RE.search(content):
        updated = _ANKI_ID_RE.sub(new_line, content)
    else:
        # Insert before the closing --- of the frontmatter block
        updated = content.replace("\n---\n", f"\n{new_line}\n---\n", 1)
    path.write_text(updated, encoding="utf-8")


def write_annotations(
    annotations: list[Annotation],
    directory: Path,
    figure_data: FigureMap | None = None,
) -> list[Path]:
    """Write each annotation to its own markdown file.

    Raises OSError on the first write failure; already-written files remain.
    Returns list of paths written.
    """
    paths: list[Path] = []
    for a in annotations:
        paths.append(write_annotation(a, directory, figure_data))
    return paths

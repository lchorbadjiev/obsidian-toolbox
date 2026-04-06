"""Writer for annotation markdown files."""
import re
from pathlib import Path

from otb.parser import Annotation

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


def write_annotation(a: Annotation, directory: Path) -> Path:
    """Write a single annotation to a markdown file in directory.

    The directory is created if it does not exist. Returns the path written.
    """
    directory.mkdir(parents=True, exist_ok=True)
    if a.title:
        filename = f"{a.number:03d} - {_sanitize(a.title)}.md"
    else:
        filename = f"{a.number:03d}.md"
    path = directory / filename
    path.write_text(_render(a), encoding="utf-8")
    return path


def write_annotations(annotations: list[Annotation], directory: Path) -> list[Path]:
    """Write each annotation to its own markdown file.

    Raises OSError on the first write failure; already-written files remain.
    Returns list of paths written.
    """
    paths: list[Path] = []
    for a in annotations:
        paths.append(write_annotation(a, directory))
    return paths

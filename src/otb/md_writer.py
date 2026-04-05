"""Writer for highlight markdown files."""
import re
from pathlib import Path

from otb.parser import Highlight

_UNSAFE_RE = re.compile(r'[/\\:*?"<>|]')
_FILENAME_MAX = 60


def _sanitize(title: str) -> str:
    """Replace filename-unsafe characters and truncate."""
    sanitized = _UNSAFE_RE.sub("-", title)
    return sanitized[:_FILENAME_MAX]


def _render(h: Highlight) -> str:
    """Render a Highlight as a markdown string."""
    lines = [
        "---",
        f'source: "{h.book.title}"',
        f"author: {h.book.author}",
        f'chapter: "{h.chapter}"',
        f"page: {h.page}",
        f"location: {h.location}",
        "type: highlight",
        f"number: {h.number}",
        "---",
        "",
    ]
    if h.title:
        lines.append(f"# {h.title}")
        lines.append("")
    lines.append(f"> {h.text}")
    lines.append("")
    return "\n".join(lines)


def write_highlight(h: Highlight, directory: Path) -> Path:
    """Write a single highlight to a markdown file in directory.

    The directory is created if it does not exist. Returns the path written.
    """
    directory.mkdir(parents=True, exist_ok=True)
    if h.title:
        filename = f"{h.number:03d} - {_sanitize(h.title)}.md"
    else:
        filename = f"{h.number:03d}.md"
    path = directory / filename
    path.write_text(_render(h), encoding="utf-8")
    return path


def write_highlights(highlights: list[Highlight], directory: Path) -> list[Path]:
    """Write each highlight to its own markdown file.

    Raises OSError on the first write failure; already-written files remain.
    Returns list of paths written.
    """
    paths: list[Path] = []
    for h in highlights:
        paths.append(write_highlight(h, directory))
    return paths

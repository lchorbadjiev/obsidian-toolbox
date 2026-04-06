"""Aspell-based word concatenation fixer for Zotero exports."""
import re
import shutil
import subprocess
import sys

_ALLOWLIST = frozenset({
    "superclass", "subclass", "subclasses", "superclasses",
    "codebase", "codebases",
    "tradeoff", "tradeoffs",
    "refactorings",
    "changelog", "changelogs",
    "runtime", "runtimes",
    "namespace", "namespaces",
    "metadata",
    "dataset", "datasets",
    "workflow", "workflows",
    "lifecycle",
    "middleware",
    "timestamp", "timestamps",
    "filename", "filenames",
    "hostname", "hostnames",
    "username", "usernames",
    "whitespace",
    "substring", "substrings",
    "multiline",
    "boolean",
    "lookup", "lookups",
    "dropdown", "dropdowns",
    "checkbox", "checkboxes",
    "tooltip", "tooltips",
    "frontend", "backend",
    "microservice", "microservices",
    "startup", "startups",
    "cleanup", "cleanups",
    "setup", "setups",
    "inline",
    "offline", "online",
    "standalone",
    "breakpoint", "breakpoints",
    "endpoint", "endpoints",
    "hotfix", "hotfixes",
    "workaround", "workarounds",
    "downgrade", "downgrades",
    "rollback", "rollbacks",
    "uptime", "downtime",
    "precompute", "precomputed",
    "refactor", "refactored",
})

_WORD_RE = re.compile(r"\S+")
_MIN_HALF_LEN = 2


def check_aspell_available() -> None:
    """Raise RuntimeError if aspell is not installed."""
    if shutil.which("aspell") is None:
        raise RuntimeError(
            "aspell not found. Install it with: brew install aspell "
            "(macOS) or apt-get install aspell aspell-en (Linux)"
        )


def _get_replacements(words: set[str]) -> dict[str, str]:
    """Run aspell pipe mode and return a replacement map for concatenated words."""
    if not words:
        return {}

    proc = subprocess.run(  # noqa: S603
        ["aspell", "-a"],
        input="\n".join(words),
        capture_output=True,
        text=True,
        check=False,
    )

    replacements: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if not line.startswith("&"):
            continue
        # Format: & word count offset: suggestion1, suggestion2, ...
        parts = line.split(": ", 1)
        if len(parts) != 2:
            continue
        original = line.split()[1]
        if original.lower() in _ALLOWLIST:
            continue
        suggestions = parts[1].split(", ")
        for suggestion in suggestions[:3]:
            if " " in suggestion and "-" not in suggestion:
                halves = suggestion.split(" ", 1)
                if all(len(h) >= _MIN_HALF_LEN for h in halves):
                    replacements[original] = suggestion
                break

    return replacements


def fix_concatenated_words(
    texts: list[str], verbose: bool = False,
) -> tuple[list[str], int]:
    """Fix concatenated words in a list of texts using aspell.

    Returns a tuple of (cleaned texts, total fix count).
    """
    if not texts:
        return [], 0

    # Collect unique tokens across all texts
    all_tokens: set[str] = set()
    for text in texts:
        all_tokens.update(_WORD_RE.findall(text))

    # Find misspelled words via aspell list
    proc = subprocess.run(  # noqa: S603
        ["aspell", "list"],
        input=" ".join(all_tokens),
        capture_output=True,
        text=True,
        check=False,
    )
    misspelled = {
        w for w in proc.stdout.strip().split("\n")
        if w and w.lower() not in _ALLOWLIST
    }

    if not misspelled:
        return list(texts), 0

    # Get replacement suggestions
    replacements = _get_replacements(misspelled)

    if not replacements:
        return list(texts), 0

    if verbose:
        for original, fixed in sorted(replacements.items()):
            print(
                f"  '{original}' \u2192 '{fixed}'",
                file=sys.stderr,
            )

    # Apply replacements to each text
    fix_count = 0
    result: list[str] = []
    for text in texts:
        new_text = text
        for original, fixed in replacements.items():
            if original in new_text:
                new_text = new_text.replace(original, fixed)
                fix_count += 1
        result.append(new_text)

    return result, fix_count

"""AnkiConnect client and annotation export service."""
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from otb.md_writer import write_anki_id
from otb.parser import Annotation

_ANKI_VERSION = 6
_FRONT_MAX = 60


class AnkiConnectError(Exception):
    """Raised when AnkiConnect is unreachable or returns an error."""


@dataclass(frozen=True)
class ExportResult:
    """Summary of an annotation export operation."""

    created: int
    skipped: int
    failed: int


class AnkiClient:
    """Thin wrapper around the AnkiConnect local REST API."""

    def __init__(self, url: str = "http://localhost:8765") -> None:
        self.url = url

    def _call(self, action: str, **params: Any) -> Any:
        payload = json.dumps(
            {"action": action, "version": _ANKI_VERSION, "params": params}
        ).encode()
        req = urllib.request.Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = json.loads(resp.read())
        except urllib.error.URLError as exc:
            raise AnkiConnectError(
                f"Cannot connect to Anki at {self.url}. "
                "Make sure Anki is running with the AnkiConnect add-on installed."
            ) from exc
        if body.get("error") is not None:
            raise AnkiConnectError(body["error"])
        return body["result"]

    def create_deck(self, deck: str) -> None:
        """Create an Anki deck (idempotent — safe to call if it already exists)."""
        self._call("createDeck", deck=deck)

    def add_notes(self, notes: list[dict[str, Any]]) -> list[int | None]:
        """Add notes to Anki. Returns a list of note IDs; None for duplicates."""
        result: list[int | None] = self._call("addNotes", notes=notes)
        return result

    def notes_info(
        self, note_ids: list[int]
    ) -> list[dict[str, Any] | None]:
        """Return note info for each ID; None where the note does not exist."""
        result: list[dict[str, Any] | None] = self._call(
            "notesInfo", notes=note_ids
        )
        return result


def build_card(annotation: Annotation, deck_name: str) -> dict[str, Any]:
    """Build an AnkiConnect note dict from an Annotation."""
    if annotation.title:
        if annotation.chapter:
            front = f"{annotation.chapter} — {annotation.title}"
        else:
            front = annotation.title
    else:
        text = annotation.text
        if len(text) > _FRONT_MAX:
            front = text[:_FRONT_MAX] + "…"
        else:
            front = text
    return {
        "deckName": deck_name,
        "modelName": "Basic",
        "fields": {"Front": front, "Back": annotation.text},
        "options": {"allowDuplicate": False},
    }


def export_annotations(  # pylint: disable=too-many-locals  # orchestrates multi-step export; variables track distinct state
    annotated_paths: list[tuple[Path, Annotation]],
    deck: str,
    anki_url: str,
) -> ExportResult:
    """Export annotations to Anki and write note IDs back to markdown files.

    Annotations with blank text are skipped. Annotations with a non-null
    anki_id are verified against Anki; those whose note still exists are
    skipped. Stale IDs (note deleted) are treated as new.
    """
    client = AnkiClient(url=anki_url)
    client.create_deck(deck)

    # Partition: skip blank text; separate into has-id and no-id
    blank_count = 0
    with_id: list[tuple[Path, Annotation]] = []
    without_id: list[tuple[Path, Annotation]] = []

    for path, annotation in annotated_paths:
        if not annotation.text.strip():
            blank_count += 1
            continue
        if annotation.anki_id is not None:
            with_id.append((path, annotation))
        else:
            without_id.append((path, annotation))

    # Verify existing IDs — skip confirmed, re-add stale
    skip_count = 0
    if with_id:
        ids = [a.anki_id for _, a in with_id]
        info = client.notes_info(ids)  # type: ignore[arg-type]
        for (path, annotation), note_data in zip(with_id, info):
            if note_data is not None:
                skip_count += 1
            else:
                without_id.append((path, annotation))

    if not without_id:
        return ExportResult(
            created=0, skipped=skip_count + blank_count, failed=0
        )

    # Batch create new cards
    notes = [build_card(a, deck) for _, a in without_id]
    results = client.add_notes(notes)

    created = 0
    failed = 0
    for (path, _), note_id in zip(without_id, results):
        if note_id is None:
            failed += 1
            continue
        created += 1
        try:
            write_anki_id(path, note_id)
        except OSError as exc:
            click.echo(
                f"Warning: could not write anki_id to {path}: {exc}", err=True
            )

    return ExportResult(
        created=created, skipped=skip_count + blank_count, failed=failed
    )

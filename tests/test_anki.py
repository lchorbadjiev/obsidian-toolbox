# pylint: disable=missing-function-docstring
"""Tests for the Anki export module."""
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from otb.anki import (
    AnkiClient,
    AnkiConnectError,
    ExportResult,
    build_card,
    export_annotations,
)
from otb.parser import Annotation, Book


def _annotation(
    text: str = "Some annotation text.",
    title: str = "Some Title",
    chapter: str = "Chapter One",
    anki_id: int | None = None,
    number: int = 1,
) -> Annotation:
    return Annotation(
        book=Book(title="My Book", author="Jane Doe"),
        chapter=chapter,
        page="1",
        location=100,
        text=text,
        title=title,
        number=number,
        anki_id=anki_id,
    )


# ---------------------------------------------------------------------------
# build_card
# ---------------------------------------------------------------------------


def test_build_card_with_chapter_and_title() -> None:
    card = build_card(_annotation(chapter="Ch 1", title="My Title"), "Deck")
    assert card["fields"]["Front"] == "Ch 1 — My Title"
    assert card["fields"]["Back"] == "Some annotation text."


def test_build_card_without_chapter() -> None:
    card = build_card(_annotation(chapter="", title="My Title"), "Deck")
    assert card["fields"]["Front"] == "My Title"


def test_build_card_empty_title_falls_back_to_text() -> None:
    long_text = "A" * 80
    card = build_card(_annotation(title="", text=long_text), "Deck")
    front = card["fields"]["Front"]
    assert len(front) <= 63  # 60 chars + ellipsis
    assert front.endswith("…")


def test_build_card_short_text_no_ellipsis() -> None:
    card = build_card(_annotation(title="", text="Short."), "Deck")
    assert card["fields"]["Front"] == "Short."


def test_build_card_deck_name() -> None:
    card = build_card(_annotation(), "My Deck")
    assert card["deckName"] == "My Deck"
    assert card["modelName"] == "Basic"
    assert card["options"]["allowDuplicate"] is False


# ---------------------------------------------------------------------------
# AnkiClient._call
# ---------------------------------------------------------------------------


def _make_response(result: object, error: object = None) -> MagicMock:
    body = json.dumps({"result": result, "error": error}).encode()
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_anki_client_call_success() -> None:
    with patch("urllib.request.urlopen", return_value=_make_response(42)):
        client = AnkiClient()
        result = client._call("version")  # pylint: disable=protected-access
    assert result == 42


def test_anki_client_call_error_field_raises() -> None:
    with patch(
        "urllib.request.urlopen",
        return_value=_make_response(None, error="deck not found"),
    ):
        client = AnkiClient()
        with pytest.raises(AnkiConnectError, match="deck not found"):
            client._call("createDeck", deck="x")  # pylint: disable=protected-access


def test_anki_client_connection_refused_raises() -> None:
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("Connection refused"),
    ):
        client = AnkiClient()
        with pytest.raises(AnkiConnectError, match="Cannot connect"):
            client._call("version")  # pylint: disable=protected-access


def test_anki_client_custom_url() -> None:
    client = AnkiClient(url="http://localhost:9999")
    assert client.url == "http://localhost:9999"


# ---------------------------------------------------------------------------
# export_annotations
# ---------------------------------------------------------------------------


def _simple_file(tmp_path: Path, number: int, anki_id: int | None = None) -> Path:
    aid_line = f"anki_id: {anki_id}\n" if anki_id is not None else ""
    content = (
        "---\n"
        'source: "My Book"\n'
        "author: Jane Doe\n"
        'chapter: "Ch"\n'
        "page: 1\n"
        "location: 1\n"
        "type: annotation\n"
        f"number: {number}\n"
        f"{aid_line}"
        "---\n\n"
        "> Real text.\n"
    )
    path = tmp_path / f"{number:03d}.md"
    path.write_text(content, encoding="utf-8")
    return path


def test_export_all_new_cards_created(tmp_path: Path) -> None:
    def mock_call(action: str, **_params: object) -> object:
        if action == "createDeck":
            return 1
        if action == "addNotes":
            notes_list = _params["notes"]
            assert isinstance(notes_list, list)
            return [i + 1000 for i in range(len(notes_list))]
        if action == "notesInfo":
            return []
        raise AnkiConnectError(f"unexpected: {action}")

    pairs = [
        (_simple_file(tmp_path, i), _annotation(number=i)) for i in range(1, 4)
    ]
    with patch("otb.anki.AnkiClient._call", side_effect=mock_call):
        result = export_annotations(pairs, "My Book", "http://localhost:8765")

    assert isinstance(result, ExportResult)
    assert result.created == 3
    assert result.skipped == 0
    assert result.failed == 0


def test_export_blank_text_skipped(tmp_path: Path) -> None:
    def mock_call(action: str, **_params: object) -> object:
        if action == "createDeck":
            return 1
        if action == "addNotes":
            return [1001]
        if action == "notesInfo":
            return []
        raise AnkiConnectError(f"unexpected: {action}")

    f1 = _simple_file(tmp_path, 1)
    f2 = _simple_file(tmp_path, 2)
    blank = _annotation(text="   ", number=1)
    good = _annotation(text="Real text.", number=2)

    with patch("otb.anki.AnkiClient._call", side_effect=mock_call):
        result = export_annotations([(f1, blank), (f2, good)], "B", "http://localhost:8765")

    assert result.created == 1
    assert result.skipped == 1


def test_export_write_back_oserror_counts_as_created(tmp_path: Path) -> None:
    def mock_call(action: str, **_params: object) -> object:
        if action == "createDeck":
            return 1
        if action == "addNotes":
            return [9999]
        if action == "notesInfo":
            return []
        raise AnkiConnectError(f"unexpected: {action}")

    f = _simple_file(tmp_path, 1)
    a = _annotation(number=1)

    with patch("otb.anki.AnkiClient._call", side_effect=mock_call):
        with patch("otb.anki.write_anki_id", side_effect=OSError("read-only")):
            result = export_annotations([(f, a)], "B", "http://localhost:8765")

    assert result.created == 1
    assert result.failed == 0


def test_export_anki_unreachable_raises(tmp_path: Path) -> None:
    f = _simple_file(tmp_path, 1)
    a = _annotation(number=1)

    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("refused"),
    ):
        with pytest.raises(AnkiConnectError):
            export_annotations([(f, a)], "B", "http://localhost:8765")


# ---------------------------------------------------------------------------
# AnkiClient.notes_info (US3)
# ---------------------------------------------------------------------------


def test_notes_info_returns_list() -> None:
    response = [{"noteId": 1001, "fields": {}}, None]
    with patch(
        "urllib.request.urlopen",
        return_value=_make_response(response),
    ):
        client = AnkiClient()
        result = client.notes_info([1001, 9999])
    assert result == response


# ---------------------------------------------------------------------------
# export_annotations — stale anki_id (US3)
# ---------------------------------------------------------------------------


def test_export_existing_anki_id_skipped(tmp_path: Path) -> None:
    def mock_call(action: str, **_params: object) -> object:
        if action == "createDeck":
            return 1
        if action == "notesInfo":
            return [{"noteId": 8888, "fields": {}}]
        if action == "addNotes":
            return []
        raise AnkiConnectError(f"unexpected: {action}")

    f = _simple_file(tmp_path, 1, anki_id=8888)
    a = _annotation(anki_id=8888, number=1)

    with patch("otb.anki.AnkiClient._call", side_effect=mock_call):
        result = export_annotations([(f, a)], "B", "http://localhost:8765")

    assert result.skipped == 1
    assert result.created == 0


def test_export_stale_anki_id_recreated(tmp_path: Path) -> None:
    def mock_call(action: str, **_params: object) -> object:
        if action == "createDeck":
            return 1
        if action == "notesInfo":
            return [None]
        if action == "addNotes":
            return [9001]
        raise AnkiConnectError(f"unexpected: {action}")

    f = _simple_file(tmp_path, 1, anki_id=7777)
    a = _annotation(anki_id=7777, number=1)

    with patch("otb.anki.AnkiClient._call", side_effect=mock_call):
        result = export_annotations([(f, a)], "B", "http://localhost:8765")

    assert result.created == 1
    assert result.skipped == 0
    assert "anki_id: 9001" in f.read_text(encoding="utf-8")

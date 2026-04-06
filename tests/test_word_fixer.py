"""Tests for the aspell-based word concatenation fixer."""
# pylint: disable=missing-function-docstring
from unittest.mock import patch

import pytest

from otb.word_fixer import check_aspell_available, fix_concatenated_words


# ---------------------------------------------------------------------------
# T002: check_aspell_available
# ---------------------------------------------------------------------------


def test_check_aspell_available_raises_when_missing() -> None:
    with patch("otb.word_fixer.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="aspell"):
            check_aspell_available()


def test_check_aspell_available_passes_when_found() -> None:
    with patch("otb.word_fixer.shutil.which", return_value="/usr/bin/aspell"):
        check_aspell_available()


# ---------------------------------------------------------------------------
# T004: basic word splitting
# ---------------------------------------------------------------------------


def test_split_concatenated_word() -> None:
    texts, count = fix_concatenated_words(["isthat is fine"])
    assert texts == ["is that is fine"]
    assert count == 1


def test_split_mixed_case() -> None:
    texts, count = fix_concatenated_words(["SoftwareWithout refactoring"])
    assert "Software Without" in texts[0]
    assert count >= 1


# ---------------------------------------------------------------------------
# T005: legitimate words unchanged
# ---------------------------------------------------------------------------


def test_legitimate_words_unchanged() -> None:
    texts, count = fix_concatenated_words(
        ["cannot without into himself"]
    )
    assert texts == ["cannot without into himself"]
    assert count == 0


# ---------------------------------------------------------------------------
# T006: allowlisted words unchanged
# ---------------------------------------------------------------------------


def test_allowlisted_words_unchanged() -> None:
    texts, count = fix_concatenated_words(
        ["the superclass and codebase are fine"]
    )
    assert "superclass" in texts[0]
    assert "codebase" in texts[0]
    assert count == 0


# ---------------------------------------------------------------------------
# T007: empty input
# ---------------------------------------------------------------------------


def test_empty_input() -> None:
    texts, count = fix_concatenated_words([])
    assert not texts
    assert count == 0


# ---------------------------------------------------------------------------
# T019: verbose output
# ---------------------------------------------------------------------------


def test_verbose_prints_splits(capfd: pytest.CaptureFixture[str]) -> None:
    fix_concatenated_words(["isthat"], verbose=True)
    captured = capfd.readouterr()
    assert "'isthat'" in captured.err
    assert "'is that'" in captured.err

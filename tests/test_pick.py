from unittest.mock import patch

import pytest

from wikibee.commands.extract import _interactive_pick_sections


@pytest.fixture
def mock_console():
    with patch("wikibee.commands.extract.console") as mock:
        yield mock


def test_interactive_pick_all(mock_console):
    text = "Intro text\n== Section 1 ==\nContent 1\n== Section 2 ==\nContent 2"
    mock_console.input.return_value = "all"

    result = _interactive_pick_sections(text)
    assert result == text


def test_interactive_pick_specific(mock_console):
    text = "Intro text\n== Section 1 ==\nContent 1\n== Section 2 ==\nContent 2"
    # Select Intro (1) and Section 2 (3)
    mock_console.input.return_value = "1, 3"

    result = _interactive_pick_sections(text)

    # Expected: Intro body + Section 2 with header
    # Intro body: "Intro text"
    # Section 2: "== Section 2 ==\nContent 2"
    expected = "Intro text\n\n== Section 2 ==\nContent 2"
    assert result == expected


def test_interactive_pick_range(mock_console):
    text = "Intro\n== S1 ==\nC1\n== S2 ==\nC2\n== S3 ==\nC3"
    # Select 2-3 (S1 and S2)
    mock_console.input.return_value = "2-3"

    result = _interactive_pick_sections(text)
    expected = "== S1 ==\nC1\n\n== S2 ==\nC2"
    assert result == expected


def test_interactive_pick_quit(mock_console):
    text = "Intro"
    mock_console.input.return_value = "q"
    result = _interactive_pick_sections(text)
    assert result == ""

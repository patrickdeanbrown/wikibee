"""Tests for Wikipedia search functionality."""

from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock

from wiki_extractor.cli import _handle_search, _show_search_menu
from wiki_extractor.client import WikiClient


class TestWikiClientSearch:
    """Test WikiClient search functionality."""

    def test_search_articles_success(self):
        """Test successful search with multiple results."""
        client = WikiClient()

        # Mock OpenSearch API response
        mock_response = [
            "test query",
            ["Result 1", "Result 2", "Result 3"],
            ["Description 1", "Description 2", "Description 3"],
            [
                "https://en.wikipedia.org/wiki/Result_1",
                "https://en.wikipedia.org/wiki/Result_2",
                "https://en.wikipedia.org/wiki/Result_3",
            ],
        ]

        with requests_mock.Mocker() as m:
            m.get("https://en.wikipedia.org/w/api.php", json=mock_response)

            results = client.search_articles("test query")

            assert len(results) == 3
            assert results[0]["title"] == "Result 1"
            assert results[0]["description"] == "Description 1"
            assert results[0]["url"] == "https://en.wikipedia.org/wiki/Result_1"

    def test_search_articles_no_results(self):
        """Test search with no results."""
        client = WikiClient()

        mock_response = ["test query", [], [], []]

        with requests_mock.Mocker() as m:
            m.get("https://en.wikipedia.org/w/api.php", json=mock_response)

            results = client.search_articles("nonexistent")

            assert results == []

    def test_search_articles_malformed_response(self):
        """Test search with malformed API response."""
        client = WikiClient()

        mock_response = ["incomplete"]  # Missing expected array elements

        with requests_mock.Mocker() as m:
            m.get("https://en.wikipedia.org/w/api.php", json=mock_response)

            results = client.search_articles("test")

            assert results == []

    def test_search_articles_network_error(self):
        """Test search with network error."""
        client = WikiClient()

        with requests_mock.Mocker() as m:
            m.get(
                "https://en.wikipedia.org/w/api.php",
                exc=requests.RequestException("Network error"),
            )

            with pytest.raises(requests.RequestException):
                client.search_articles("test")


class TestSearchHandling:
    """Test CLI search handling logic."""

    @patch("wiki_extractor.cli.WikiClient")
    def test_handle_search_single_result(self, mock_client_class, capsys):
        """Test auto-selection when single result found."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.search_articles.return_value = [
            {
                "title": "Test Article",
                "url": "https://en.wikipedia.org/wiki/Test_Article",
            }
        ]

        args = MagicMock()
        args.timeout = 15

        result = _handle_search("test", args)

        assert result == "https://en.wikipedia.org/wiki/Test_Article"
        captured = capsys.readouterr()
        assert "Found exact match" in captured.out

    @patch("wiki_extractor.cli.WikiClient")
    def test_handle_search_no_results(self, mock_client_class, capsys):
        """Test handling when no results found."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.search_articles.return_value = []

        args = MagicMock()
        args.timeout = 15

        result = _handle_search("nonexistent", args)

        assert result is None
        captured = capsys.readouterr()
        assert "No results found" in captured.out

    @patch("wiki_extractor.cli.WikiClient")
    def test_handle_search_yolo_multiple_results(self, mock_client_class, capsys):
        """Test --yolo flag auto-selects first result."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.search_articles.return_value = [
            {
                "title": "First Result",
                "url": "https://en.wikipedia.org/wiki/First_Result",
            },
            {
                "title": "Second Result",
                "url": "https://en.wikipedia.org/wiki/Second_Result",
            },
        ]

        args = MagicMock()
        args.timeout = 15
        args.yolo = True

        result = _handle_search("test", args)

        assert result == "https://en.wikipedia.org/wiki/First_Result"
        captured = capsys.readouterr()
        assert "Auto-selected" in captured.out

    @patch("wiki_extractor.cli.WikiClient")
    def test_handle_search_network_error(self, mock_client_class, capsys):
        """Test handling network errors gracefully."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_client.search_articles.side_effect = requests.RequestException(
            "Network error"
        )

        args = MagicMock()
        args.timeout = 15

        result = _handle_search("test", args)

        assert result is None
        captured = capsys.readouterr()
        assert "Search failed" in captured.out


class TestSearchMenu:
    """Test interactive search menu."""

    @patch("builtins.input", return_value="1")
    def test_show_search_menu_valid_selection(self, mock_input, capsys):
        """Test valid menu selection."""
        results = [
            {"title": "Result 1", "url": "https://en.wikipedia.org/wiki/Result_1"},
            {"title": "Result 2", "url": "https://en.wikipedia.org/wiki/Result_2"},
        ]

        url = _show_search_menu(results, "test")

        assert url == "https://en.wikipedia.org/wiki/Result_1"
        captured = capsys.readouterr()
        assert "Found 2 results" in captured.out
        assert "Selected: Result 1" in captured.out

    @patch("builtins.input", return_value="q")
    def test_show_search_menu_quit(self, mock_input, capsys):
        """Test quitting from menu."""
        results = [
            {"title": "Result 1", "url": "https://en.wikipedia.org/wiki/Result_1"}
        ]

        url = _show_search_menu(results, "test")

        assert url is None
        captured = capsys.readouterr()
        assert "Cancelled" in captured.out

    @patch("builtins.input", side_effect=["invalid", "99", "1"])
    def test_show_search_menu_invalid_then_valid(self, mock_input, capsys):
        """Test handling invalid input then valid selection."""
        results = [
            {"title": "Result 1", "url": "https://en.wikipedia.org/wiki/Result_1"}
        ]

        url = _show_search_menu(results, "test")

        assert url == "https://en.wikipedia.org/wiki/Result_1"
        captured = capsys.readouterr()
        assert "Please enter a valid number" in captured.out
        assert "Please enter a number between 1 and 1" in captured.out

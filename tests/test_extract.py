import os
import sys

import pytest

# Ensure project root is on sys.path so extract.py can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extract import (
    INFLECT_AVAILABLE,
    NetworkError,
    extract_wikipedia_text,
    make_tts_friendly,
    normalize_for_tts,
    sanitize_filename,
)


def test_sanitize_filename_basic():
    assert sanitize_filename("My File: Test/?") == "My_File_Test"


def test_sanitize_filename_reserved_name():
    assert sanitize_filename("CON") != "CON"


def test_sanitize_filename_truncation():
    s = "a" * 200
    out = sanitize_filename(s)
    assert len(out) <= 100


def test_make_tts_friendly_header_and_link():
    md = (
        "# Title\n\n"
        "This is a paragraph with a [link](http://example.com) and *emphasis* "
        "and `code`."
    )
    tts = make_tts_friendly(md)
    assert "Title." in tts
    assert "This is a paragraph with a link and emphasis and code." in tts


def test_normalize_for_tts_basic():
    raw = "  Line1\n\n\n  Line2 *italic*  "
    out = normalize_for_tts(raw)
    assert "Line1" in out and "Line2" in out


def test_extract_wikipedia_text_with_fake_session():
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "query": {
                    "pages": {
                        "123": {
                            "title": "Test Page",
                            "extract": "This is content.",
                        }
                    }
                }
            }

    class FakeSession:
        def get(self, url, params=None, timeout=None):
            return FakeResp()

    text, title = extract_wikipedia_text(
        "https://en.wikipedia.org/wiki/Test_Page", session=FakeSession()
    )
    assert title == "Test Page"
    assert "This is content." in text


def test_number_conversion_if_inflect_available():
    # If inflect is installed, normalize_for_tts should convert digits to words
    # when requested
    if INFLECT_AVAILABLE:
        out = normalize_for_tts("There are 3 cats.", convert_numbers=True)
        assert "three" in out.lower()
    else:
        pytest.skip("inflect not available")


def test_extract_raises_network_error_when_requested():
    class BadSession:
        def get(self, url, params=None, timeout=None):
            raise requests.exceptions.RequestException("net")

    # import requests locally to construct exception
    import requests

    with pytest.raises(NetworkError):
        extract_wikipedia_text(
            "https://en.wikipedia.org/wiki/Test_Page",
            session=BadSession(),
            raise_on_error=True,
        )

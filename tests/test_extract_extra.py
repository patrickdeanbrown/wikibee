import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from extract import (
    APIError,
    DisambiguationError,
    NotFoundError,
    extract_wikipedia_text,
    write_text_file,
)


def test_disambiguation_detection_returns_none():
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "query": {
                    "pages": {
                        "123": {
                            "title": "Apple",
                            "pageprops": {"disambiguation": ""},
                            "extract": "Apple may refer to:",
                        }
                    }
                }
            }

    class FakeSession:
        def get(self, url, params=None, timeout=None):
            return FakeResp()

    # default behavior: should return (None, title)
    text, title = extract_wikipedia_text(
        "https://en.wikipedia.org/wiki/Apple",
        session=FakeSession(),
    )
    assert title == "Apple"
    assert text is None


def test_disambiguation_detection_raises_when_requested():
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "query": {
                    "pages": {
                        "123": {
                            "title": "Apple",
                            "pageprops": {"disambiguation": ""},
                            "extract": "Apple may refer to:",
                        }
                    }
                }
            }

    class FakeSession:
        def get(self, url, params=None, timeout=None):
            return FakeResp()

    with pytest.raises(DisambiguationError):
        extract_wikipedia_text(
            "https://en.wikipedia.org/wiki/Apple",
            session=FakeSession(),
            raise_on_error=True,
        )


def test_write_text_file_prevents_path_traversal(tmp_path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    dangerous = os.path.join(str(out_dir), "..", "evil.md")
    content = "hi"
    with pytest.raises(ValueError):
        write_text_file(dangerous, str(out_dir), content)

    # safe path should write
    safe_path = os.path.join(str(out_dir), "good.md")
    write_text_file(safe_path, str(out_dir), content)
    assert os.path.exists(safe_path)


def test_extract_raises_notfound_when_requested():
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"query": {"pages": {"123": {"title": "Ghost", "extract": None}}}}

    class FakeSession:
        def get(self, url, params=None, timeout=None):
            return FakeResp()

    with pytest.raises(NotFoundError):
        extract_wikipedia_text(
            "https://en.wikipedia.org/wiki/Ghost",
            session=FakeSession(),
            raise_on_error=True,
        )


def test_extract_raises_api_error_on_bad_json():
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            raise json.JSONDecodeError("msg", "doc", 0)

    class FakeSession:
        def get(self, url, params=None, timeout=None):
            return FakeResp()

    with pytest.raises(APIError):
        extract_wikipedia_text(
            "https://en.wikipedia.org/wiki/Broken",
            session=FakeSession(),
            raise_on_error=True,
        )

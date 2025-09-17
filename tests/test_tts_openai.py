import os
from pathlib import Path

import pytest

from wikibee import tts_openai
from wikibee.tts_openai import TTSClientError, TTSOpenAIClient


class FakeResponse:
    def __init__(self, data: bytes):
        self._data = data
        self.streamed_to = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def stream_to_file(self, path: str):
        # write binary data to path to simulate streaming
        self.streamed_to = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(self._data)


class FakeCreate:
    def __init__(self, captured, data: bytes = b"audio-bytes"):
        self.captured = captured
        self.data = data

    def __call__(self, **kwargs):
        # capture the kwargs and return a context manager
        self.captured.update(kwargs)
        return FakeResponse(self.data)


class FakeOpenAIClient:
    def __init__(self, captured: dict, data: bytes = b"audio-bytes"):
        # build the nested attribute chain audio.speech.with_streaming_response.create
        self.captured = captured
        self._create = FakeCreate(self.captured, data=data)

        class WS:
            def __init__(self, create):
                self.create = create

        class Speech:
            def __init__(self, ws):
                self.with_streaming_response = ws

        class Audio:
            def __init__(self, speech):
                self.speech = speech

        self.audio = Audio(Speech(WS(self._create)))


def test_synthesize_to_file_success(tmp_path, monkeypatch):
    captured = {}
    fake_client = FakeOpenAIClient(captured, data=b"TEST_BYTES")

    # monkeypatch the OpenAI constructor used in the module
    monkeypatch.setattr(tts_openai, "OpenAI", lambda base_url, api_key: fake_client)

    client = TTSOpenAIClient(base_url="http://localhost:8880/v1", api_key="not-needed")
    saved = client.synthesize_to_file(
        text="Hello world",
        dest_path="out.mp3",
        base_dir=str(tmp_path),
        model="kokoro",
        voice="af_sky+af_bella",
        file_format="mp3",
    )

    expected_path = tmp_path / "out.mp3"

    assert saved == str(expected_path)
    assert expected_path.exists()
    with open(saved, "rb") as f:
        data = f.read()
    assert data == b"TEST_BYTES"

    # ensure parameters were forwarded to the OpenAI create call
    assert captured.get("model") == "kokoro"
    assert captured.get("voice") == "af_sky+af_bella"
    assert captured.get("input") == "Hello world"
    assert captured.get("format") == "mp3"


def test_synthesize_raises_on_client_error(monkeypatch):
    # simulate the OpenAI constructor raising an exception
    def bad_openai(base_url, api_key):
        raise RuntimeError("connect error")

    monkeypatch.setattr(tts_openai, "OpenAI", bad_openai)

    client = TTSOpenAIClient()
    with pytest.raises(TTSClientError):
        client.synthesize_to_file("text", dest_path="out.mp3")


def test_streaming_raises_and_bubbles(monkeypatch, tmp_path):
    # simulate a create that returns a context manager which raises when used
    class BadCreate:
        def __call__(self, **kwargs):
            class BadResp:
                def __enter__(self):
                    raise RuntimeError("stream failure")

                def __exit__(self, exc_type, exc, tb):
                    return False

            return BadResp()

    fake_client = type("C", (), {})()
    audio = type("A", (), {})()
    speech = type("S", (), {})()
    ws = type("W", (), {})()
    ws.create = BadCreate()
    speech.with_streaming_response = ws
    audio.speech = speech
    fake_client.audio = audio

    monkeypatch.setattr(tts_openai, "OpenAI", lambda base_url, api_key: fake_client)

    client = TTSOpenAIClient()
    with pytest.raises(TTSClientError):
        client.synthesize_to_file(
            "hi",
            dest_path="out.mp3",
            base_dir=str(tmp_path),
        )


def test_raises_when_dest_escapes_base(monkeypatch, tmp_path):
    monkeypatch.setattr(tts_openai, "OpenAI", lambda base_url, api_key: object())

    client = TTSOpenAIClient()

    with pytest.raises(TTSClientError):
        client.synthesize_to_file(
            "hi",
            dest_path="../out.mp3",
            base_dir=str(tmp_path),
        )


def test_synthesize_fallbacks_when_format_not_supported(tmp_path, monkeypatch):
    calls = []

    class RejectingCreate:
        def __init__(self):
            self.first_call = True

        def create(self, **kwargs):
            calls.append(kwargs.copy())
            if "format" in kwargs and self.first_call:
                self.first_call = False
                raise TypeError("create() got an unexpected keyword argument 'format'")
            return FakeResponse(b"audio")

    ws = RejectingCreate()
    speech = type("S", (), {"with_streaming_response": ws})()
    audio = type("A", (), {"speech": speech})()
    rejecting_client = type("C", (), {"audio": audio})()

    monkeypatch.setattr(
        tts_openai, "OpenAI", lambda base_url, api_key: rejecting_client
    )

    client = TTSOpenAIClient()
    saved = client.synthesize_to_file(
        "text",
        dest_path="out.mp3",
        base_dir=str(tmp_path),
        file_format="mp3",
    )

    assert Path(saved).exists()
    assert len(calls) == 2
    assert "format" in calls[0]
    assert "format" not in calls[1]

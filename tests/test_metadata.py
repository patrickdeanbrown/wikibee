import pytest
from unittest.mock import MagicMock
from pathlib import Path
from wikibee.services.output import OutputManager
from wikibee.services.tts import TTSService

class FakeTTSClient:
    def __init__(self):
        pass

    def synthesize_to_file(self, *args, **kwargs):
        # Create a dummy file
        dest_path = kwargs['dest_path']
        base_dir = kwargs['base_dir']
        path = Path(base_dir) / dest_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"dummy audio")
        return str(path)

def test_synthesize_audio_applies_metadata(monkeypatch, tmp_path):
    # Mock EasyID3
    mock_easyid3 = MagicMock()
    # When instantiated, return a dict-like object
    mock_audio = MagicMock()
    mock_audio.__setitem__ = MagicMock()
    mock_audio.save = MagicMock()
    mock_easyid3.return_value = mock_audio
    mock_easyid3.valid_keys.keys.return_value = ['title', 'artist', 'album', 'genre', 'website', 'date']

    monkeypatch.setattr("wikibee.services.tts.EasyID3", mock_easyid3)

    # Setup Service
    output_manager = OutputManager(tmp_path, audio_format="mp3")
    client = FakeTTSClient()
    service = TTSService(client=client, output_manager=output_manager)

    paths = output_manager.prepare_paths("Test Article", None)

    metadata = {
        "title": "Test Article",
        "artist": "Wikibee",
        "album": "Wikibee Articles",
        "genre": "Speech",
        "website": "http://example.com",
        "date": "2024",
    }

    service.synthesize_audio(
        markdown="# Test Article",
        paths=paths,
        heading_prefix=None,
        normalize=False,
        voice="test_voice",
        file_format="mp3",
        metadata=metadata
    )

    # Verify EasyID3 called
    assert mock_easyid3.call_count >= 1
    # Verify metadata set
    mock_audio.__setitem__.assert_any_call("title", "Test Article")
    mock_audio.__setitem__.assert_any_call("artist", "Wikibee")
    mock_audio.__setitem__.assert_any_call("album", "Wikibee Articles")
    mock_audio.__setitem__.assert_any_call("website", "http://example.com")
    mock_audio.save.assert_called()

def test_synthesize_m4b_applies_metadata(monkeypatch, tmp_path):
    # Mock ffmpeg existence
    monkeypatch.setattr("shutil.which", lambda x: "/usr/bin/ffmpeg")

    # Mock subprocess.run to side-effect create file
    mock_run = MagicMock()
    def side_effect_run(cmd, **kwargs):
        output_path = Path(cmd[-1])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"dummy m4b")
        return MagicMock()
    mock_run.side_effect = side_effect_run
    monkeypatch.setattr("subprocess.run", mock_run)

    # Mock MP3 for duration check
    mock_mp3 = MagicMock()
    mock_mp3.return_value.info.length = 10.0
    monkeypatch.setattr("wikibee.services.tts.MP3", mock_mp3)

    # Setup Service
    output_manager = OutputManager(tmp_path, audio_format="m4b")
    client = FakeTTSClient()
    service = TTSService(client=client, output_manager=output_manager)

    paths = output_manager.prepare_paths("Test Article", None)

    metadata = {
        "title": "Test Article",
        "artist": "Wikibee",
    }

    service.synthesize_audio(
        markdown="# Test Article",
        paths=paths,
        heading_prefix=None,
        normalize=False,
        voice="test_voice",
        file_format="m4b",
        metadata=metadata
    )

    assert mock_run.called
    cmd = mock_run.call_args[0][0]

    # Verify ffmetadata args
    # We check if "ffmetadata" is in command
    assert "ffmetadata" in cmd

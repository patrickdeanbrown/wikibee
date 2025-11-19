from pathlib import Path
from typing import Optional

import pytest

from wikibee.services.output import OutputManager
from wikibee.services.tts import TTSService


class FakeTTSClient:
    def __init__(self) -> None:
        self.calls = []

    def synthesize_to_file(
        self,
        text: str,
        dest_path: str,
        base_dir: str,
        model: str = "kokoro",
        voice: Optional[str] = None,
        file_format: str = "mp3",
        timeout: int = 60,
    ) -> str:
        self.calls.append(
            {
                "text": text,
                "dest_path": dest_path,
                "base_dir": base_dir,
                "voice": voice,
                "file_format": file_format,
            }
        )
        target = Path(base_dir) / dest_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"audio")
        return str(target)


@pytest.fixture()
def make_tts_service(tmp_path: Path):
    def _factory(audio_format: str = "wav") -> TTSService:
        output_manager = OutputManager(tmp_path, audio_format=audio_format)
        client = FakeTTSClient()
        return TTSService(client=client, output_manager=output_manager)

    return _factory


def test_build_tts_text_respects_heading_prefix(make_tts_service) -> None:
    tts_service = make_tts_service()
    text = tts_service.build_tts_text(
        markdown="# Intro\nContent",
        heading_prefix="Section:",
        normalize=True,
    )

    assert "Section: Intro." in text


def test_build_tts_sections_use_markdown_headings(make_tts_service) -> None:
    service = make_tts_service()
    sections = service.build_tts_sections(
        markdown="Intro text.\n\n# First\nBody\n\n## Second\nMore",
        heading_prefix="Chapter",
        normalize=False,
    )

    assert [section.title for section in sections] == [
        "Introduction",
        "First",
        "Second",
    ]
    assert sections[1].text.startswith("Chapter First.")


def test_synthesize_audio_invokes_client(make_tts_service, tmp_path: Path) -> None:
    tts_service = make_tts_service()
    manager = tts_service.output_manager
    paths = manager.prepare_paths("Audio", None)
    audio_path = tts_service.synthesize_audio(
        markdown="# Title\nBody",
        paths=paths,
        heading_prefix=None,
        normalize=False,
        voice="af_voice",
        file_format="wav",
    )

    assert Path(audio_path).exists()
    fake_client = tts_service.client  # type: ignore[attr-defined]
    assert fake_client.calls[0]["voice"] == "af_voice"
    assert fake_client.calls[0]["file_format"] == "wav"


def test_synthesize_m4b_uses_ffmpeg(monkeypatch, tmp_path: Path) -> None:
    fake_client = FakeTTSClient()
    service = TTSService(
        client=fake_client,
        output_manager=OutputManager(tmp_path, audio_format="m4b"),
    )

    monkeypatch.setattr("shutil.which", lambda cmd: "/usr/bin/ffmpeg")

    created_commands = []

    def fake_run(cmd, check):
        Path(cmd[-1]).touch()
        created_commands.append(cmd)

    monkeypatch.setattr("subprocess.run", fake_run)

    class DummyMP3:
        def __init__(self, path):
            class Info:
                length = 1.0

            self.info = Info()

    monkeypatch.setattr("wikibee.services.tts.MP3", DummyMP3)

    paths = service.output_manager.prepare_paths("Chaptered", None)
    result = service.synthesize_audio(
        markdown="# Intro\nBody\n\n# Next\nMore",
        paths=paths,
        heading_prefix="Section:",
        normalize=False,
        voice=None,
        file_format="m4b",
    )

    assert Path(result).exists()
    assert created_commands
    # two headings -> two synthesis calls
    assert len(fake_client.calls) == 2

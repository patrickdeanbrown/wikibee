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
def tts_service(tmp_path: Path) -> TTSService:
    output_manager = OutputManager(tmp_path, audio_format="wav")
    client = FakeTTSClient()
    service = TTSService(client=client, output_manager=output_manager)
    return service


def test_build_tts_text_respects_heading_prefix(tts_service: TTSService) -> None:
    text = tts_service.build_tts_text(
        markdown="# Intro\nContent",
        heading_prefix="Section:",
        normalize=True,
    )

    assert "Section: Intro." in text


def test_synthesize_audio_invokes_client(
    tts_service: TTSService, tmp_path: Path
) -> None:
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

from __future__ import annotations

from typing import Optional

from wikibee import formatting
from wikibee.services.output import OutputManager, OutputPaths
from wikibee.tts_normalizer import normalize_for_tts as tts_normalize_for_tts
from wikibee.tts_openai import TTSOpenAIClient


class TTSService:
    """Coordinate TTS-friendly text generation and audio synthesis."""

    def __init__(
        self,
        *,
        client: TTSOpenAIClient | None = None,
        output_manager: OutputManager,
        model: str = "kokoro",
        timeout: int = 60,
    ) -> None:
        self.client = client or TTSOpenAIClient()
        self.output_manager = output_manager
        self.model = model
        self.timeout = timeout

    def build_tts_text(
        self,
        markdown: str,
        *,
        heading_prefix: Optional[str],
        normalize: bool,
    ) -> str:
        source = markdown
        if normalize:
            source = tts_normalize_for_tts(source)
        return formatting.make_tts_friendly(source, heading_prefix=heading_prefix)

    def synthesize_audio(
        self,
        *,
        markdown: str,
        paths: OutputPaths,
        heading_prefix: Optional[str],
        normalize: bool,
        voice: Optional[str],
        file_format: str,
    ) -> str:
        text_for_audio = self.build_tts_text(
            markdown,
            heading_prefix=heading_prefix,
            normalize=normalize,
        )
        relative_audio_path = paths.audio_path.relative_to(self.output_manager.base_dir)
        return self.client.synthesize_to_file(
            text_for_audio,
            dest_path=str(relative_audio_path),
            base_dir=str(self.output_manager.base_dir),
            model=self.model,
            voice=voice,
            file_format=file_format,
            timeout=self.timeout,
        )

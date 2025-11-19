from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, cast

from mutagen.mp3 import MP3

from wikibee import formatting
from wikibee.services.output import OutputManager, OutputPaths
from wikibee.tts_normalizer import normalize_for_tts as tts_normalize_for_tts
from wikibee.tts_openai import TTSClientError, TTSOpenAIClient


@dataclass
class TTSSection:
    title: str
    text: str


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

    def build_tts_sections(
        self,
        markdown: str,
        *,
        heading_prefix: Optional[str],
        normalize: bool,
    ) -> list[TTSSection]:
        sections = formatting.build_tts_sections(markdown)
        results: list[TTSSection] = []
        for title, section_markdown in sections:
            source = section_markdown
            if normalize:
                source = tts_normalize_for_tts(source)
            tts_text = formatting.make_tts_friendly(
                source,
                heading_prefix=heading_prefix,
            ).strip()
            if tts_text:
                results.append(TTSSection(title=title, text=tts_text))
        return results

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
        if file_format.lower() == "m4b":
            return self._synthesize_m4b_with_chapters(
                markdown=markdown,
                paths=paths,
                heading_prefix=heading_prefix,
                normalize=normalize,
                voice=voice,
            )

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

    def _synthesize_m4b_with_chapters(
        self,
        *,
        markdown: str,
        paths: OutputPaths,
        heading_prefix: Optional[str],
        normalize: bool,
        voice: Optional[str],
    ) -> str:
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            raise TTSClientError(
                "ffmpeg is required to produce M4B output. Please install ffmpeg and"
                " ensure it is available on your PATH."
            )

        sections = self.build_tts_sections(
            markdown,
            heading_prefix=heading_prefix,
            normalize=normalize,
        )
        if not sections:
            sections = [
                TTSSection(
                    title="Article",
                    text=self.build_tts_text(
                        markdown,
                        heading_prefix=heading_prefix,
                        normalize=normalize,
                    ),
                )
            ]

        base_dir = Path(self.output_manager.base_dir)
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            segment_paths: list[Path] = []
            chapter_lengths: list[float] = []

            for idx, section in enumerate(sections, start=1):
                segment_name = f"segment_{idx:03d}.mp3"
                relative_segment = segment_name
                dest = tmp_path / segment_name
                self.client.synthesize_to_file(
                    section.text,
                    dest_path=relative_segment,
                    base_dir=str(tmp_path),
                    model=self.model,
                    voice=voice,
                    file_format="mp3",
                    timeout=self.timeout,
                )
                try:
                    info = cast(Any, MP3(dest))
                    if info.info is None:
                        raise TTSClientError(
                            f"Unable to read audio duration for {dest}"
                        )
                    chapter_lengths.append(float(info.info.length))
                except Exception as exc:  # pragma: no cover - defensive
                    raise TTSClientError(
                        f"Unable to read audio duration for {dest}"
                    ) from exc
                segment_paths.append(dest)

            concat_list = tmp_path / "concat.txt"
            with concat_list.open("w", encoding="utf-8") as fh:
                for path in segment_paths:
                    fh.write(f"file '{path.as_posix()}'\n")

            metadata_file = tmp_path / "chapters.ffmetadata"
            start_ms = 0
            with metadata_file.open("w", encoding="utf-8") as fh:
                fh.write(";FFMETADATA1\n")
                for section, duration in zip(sections, chapter_lengths):
                    end_ms = start_ms + int(duration * 1000)
                    fh.write("[CHAPTER]\n")
                    fh.write("TIMEBASE=1/1000\n")
                    fh.write(f"START={start_ms}\n")
                    fh.write(f"END={end_ms}\n")
                    fh.write(f"title={section.title}\n")
                    start_ms = end_ms

            final_tmp = tmp_path / "output.m4b"
            cmd = [
                ffmpeg_path,
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-f",
                "ffmetadata",
                "-i",
                str(metadata_file),
                "-map_metadata",
                "1",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                str(final_tmp),
            ]
            subprocess.run(cmd, check=True)

            relative_audio_path = paths.audio_path.relative_to(base_dir)
            final_dest = base_dir / relative_audio_path
            final_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(final_tmp), str(final_dest))
            return str(final_dest)

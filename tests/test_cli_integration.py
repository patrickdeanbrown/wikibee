from pathlib import Path
from typing import Optional

from typer.testing import CliRunner

from wikibee import cli


class DummyTTSClient:
    def __init__(self, base_url: str = "", api_key: str = "") -> None:
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
        target = Path(base_dir) / dest_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"audio-bytes")
        self.calls.append(dest_path)
        return str(target)


def test_cli_end_to_end_generates_outputs(monkeypatch, tmp_path):
    """Run CLI end-to-end with fake TTS and article content."""

    monkeypatch.setattr(
        "wikibee.commands.extract.extract_wikipedia_text",
        lambda url, **kwargs: ("Content", "Example Article"),
    )
    monkeypatch.setattr(
        "wikibee.commands.extract._handle_search",
        lambda term, args: "https://example.org/wiki/Example",
    )
    monkeypatch.setattr(
        "wikibee.commands.extract.TTSOpenAIClient",
        DummyTTSClient,
    )

    output_dir = tmp_path / "out"
    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            "Example",
            "--output",
            str(output_dir),
            "--tts",
            "--tts-audio",
            "--tts-format",
            "mp3",
            "--heading-prefix",
            "Section:",
        ],
    )

    assert result.exit_code == 0

    markdown = output_dir / "Example_Article.md"
    tts_copy = output_dir / "Example_Article.txt"
    audio_file = output_dir / "Example_Article.mp3"

    assert markdown.exists()
    assert tts_copy.exists()
    assert audio_file.exists()
    assert "Content" in markdown.read_text(encoding="utf-8")

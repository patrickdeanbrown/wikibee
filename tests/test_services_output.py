from pathlib import Path

import pytest

from wikibee.services.output import OutputManager


@pytest.fixture()
def output_manager(tmp_path: Path) -> OutputManager:
    return OutputManager(base_dir=tmp_path, audio_format="mp3")


def test_prepare_paths_generates_safe_markdown_name(
    output_manager: OutputManager,
) -> None:
    paths = output_manager.prepare_paths(page_title="Altiplano", filename=None)

    assert paths.markdown_path.suffix == ".md"
    assert paths.markdown_path.name == "Altiplano.md"
    assert paths.markdown_path.parent == output_manager.base_dir


def test_prepare_paths_avoids_collisions(output_manager: OutputManager) -> None:
    first = output_manager.prepare_paths(page_title="Duplicate", filename=None)
    first.markdown_path.write_text("sample", encoding="utf-8")

    second = output_manager.prepare_paths(page_title="Duplicate", filename=None)

    assert second.markdown_path != first.markdown_path
    assert second.markdown_path.name.startswith("Duplicate_")


def test_prepare_paths_respects_custom_filename(output_manager: OutputManager) -> None:
    paths = output_manager.prepare_paths(page_title="Ignored", filename="custom-name")

    assert paths.markdown_path.name == "custom-name.md"
    assert paths.tts_path.name == "custom-name.txt"
    assert paths.audio_path.name == "custom-name.mp3"


def test_write_markdown_creates_file(
    output_manager: OutputManager, tmp_path: Path
) -> None:
    paths = output_manager.prepare_paths(page_title="Write Test", filename=None)
    output_manager.write_markdown(paths, "# Title\nBody\n")

    assert paths.markdown_path.exists()
    assert paths.markdown_path.read_text(encoding="utf-8").startswith("# Title")


def test_write_tts_copy_respects_optional_heading_prefix(
    output_manager: OutputManager,
) -> None:
    paths = output_manager.prepare_paths(page_title="Heading", filename=None)
    output_manager.write_tts_copy(
        paths,
        markdown="# Heading\nContent",
        heading_prefix="Section:",
        normalize=True,
    )

    tts_text = paths.tts_path.read_text(encoding="utf-8")
    assert "Section: Heading." in tts_text


def test_audio_path_uses_audio_format(output_manager: OutputManager) -> None:
    paths = output_manager.prepare_paths(page_title="Audio", filename=None)
    assert paths.audio_path.suffix == ".mp3"

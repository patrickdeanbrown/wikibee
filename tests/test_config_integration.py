from pathlib import Path
from typing import Optional

from typer.testing import CliRunner

try:  # Python 3.11+
    import tomllib as tomli  # type: ignore[attr-defined]
except Exception:  # Python < 3.11
    import tomli  # type: ignore[no-redef]

from wikibee import cli, config
from wikibee.commands import extract


def test_config_precedence(monkeypatch, tmp_path):
    """
    Test the configuration precedence: CLI > config file > defaults.
    """
    # 1. Create a temporary config file
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[general]
default_timeout = 20
verbose = true
no_save = true

[tts]
default_voice = "config-voice"
normalize = true
file = true
audio = true

[search]
auto_select = true
search_limit = 6
"""
    )

    # 2. Patch get_config_path to use the temporary file
    monkeypatch.setattr(cli.config, "get_config_path", lambda: config_path)

    # 3. Capture the Args object built from config defaults
    captured_runtime: dict[str, config.RuntimeConfig] = {}

    original_merge = config.merge_configs

    def capture_merge(defaults, cfg, cli_args):
        runtime = original_merge(defaults, cfg, cli_args)
        captured_runtime["value"] = runtime
        return runtime

    monkeypatch.setattr(config, "merge_configs", capture_merge)

    # Patch output manager to avoid filesystem writes
    from wikibee.services.output import OutputPaths

    class DummyManager:
        def __init__(self, base_dir: str, audio_format: str) -> None:
            self.base_dir = Path(base_dir)
            self.paths = OutputPaths(
                markdown_path=self.base_dir / "dummy.md",
                tts_path=self.base_dir / "dummy.txt",
                audio_path=self.base_dir / f"dummy.{audio_format}",
            )

        def prepare_paths(
            self, page_title: str, filename: Optional[str]
        ) -> OutputPaths:
            return self.paths

        def write_markdown(self, paths: OutputPaths, content: str) -> None:
            pass

        def write_tts_copy(self, *args, **kwargs) -> None:
            pass

    monkeypatch.setattr(extract, "OutputManager", DummyManager)

    class DummyTTSService:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def synthesize_audio(self, **kwargs) -> str:
            return "dummy-audio.mp3"

    monkeypatch.setattr(extract, "TTSService", DummyTTSService)

    # Also patch extract_wikipedia_text to avoid network calls
    monkeypatch.setattr(
        extract,
        "extract_wikipedia_text",
        lambda url, **kwargs: ("Fake content.", "Fake Title"),
    )

    # 4. Run the CLI
    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            "https://example.org/wiki/Fake",
            "--timeout",
            "30",  # CLI override
            "--search-limit",
            "8",  # CLI override beats config value of 6
            # tts_voice is NOT provided, so config value should be used
            # lead_only is NOT provided, so default should be used
        ],
    )

    assert result.exit_code == 0

    # 5. Assert that _write_outputs was called with the correct, merged config
    runtime = captured_runtime["value"]

    # CLI override: timeout=30 should win over config file's 20
    assert runtime.timeout == 30

    # Config file value: tts_voice="config-voice" should be used
    assert runtime.tts_voice == "config-voice"

    # Default value: lead_only=False should be used
    assert runtime.lead_only is False

    # Config-driven verbosity should be respected
    assert runtime.verbose is True

    # CLI override should win for search_limit
    assert runtime.search_limit == 8

    # Config should enable yolo mode and normalization
    assert runtime.yolo is True
    assert runtime.tts_normalize is True

    # Config should enable TTS outputs and no-save mode
    assert runtime.tts_file is True
    assert runtime.tts_audio is True
    assert runtime.no_save is True


def test_config_init(monkeypatch, tmp_path):
    """
    Test that `wikibee config init` creates a default config file.
    """
    # 1. Set up a temporary path for the config file
    config_path = tmp_path / "config.toml"
    monkeypatch.setattr(cli.config, "get_config_path", lambda: config_path)

    # 2. Run the `config init` command
    runner = CliRunner()
    result = runner.invoke(cli.app, ["config", "init", "--force"])

    assert result.exit_code == 0
    assert (
        f"Default configuration file created at {config_path}"
        in result.stdout.replace("\n", "")
    )

    # 3. Verify the file was created and has the correct content
    assert config_path.exists()

    with open(config_path, "rb") as f:
        created_config = tomli.load(f)

    expected_config = {
        "general": {
            "output_dir": str(Path.home() / "wikibee"),
            "default_timeout": int(cli.DEFAULTS["timeout"]),
            "lead_only": bool(cli.DEFAULTS["lead_only"]),
            "no_save": bool(cli.DEFAULTS["no_save"]),
            "verbose": bool(cli.DEFAULTS["verbose"]),
        },
        "tts": {
            "server_url": str(cli.DEFAULTS["tts_server"]),
            "default_voice": str(cli.DEFAULTS["tts_voice"]),
            "format": str(cli.DEFAULTS["tts_format"]),
            "normalize": bool(cli.DEFAULTS["tts_normalize"]),
            "file": bool(cli.DEFAULTS["tts_file"]),
            "audio": bool(cli.DEFAULTS["tts_audio"]),
        },
        "search": {
            "auto_select": bool(cli.DEFAULTS["yolo"]),
            "search_limit": int(cli.DEFAULTS["search_limit"]),
        },
    }

    assert created_config == expected_config

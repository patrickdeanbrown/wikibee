from typer.testing import CliRunner


def test_cli_runs(monkeypatch):
    """Ensure the Typer CLI can be invoked without errors."""

    def fake_extract(url, **kwargs):
        return ("Fake content.", "Fake Title")

    import wikibee.cli as cli

    monkeypatch.setattr(cli, "extract_wikipedia_text", fake_extract)

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        ["https://example.org/wiki/Fake", "--no-save"],
    )

    assert result.exit_code == 0
    assert "Fake content." in result.stdout

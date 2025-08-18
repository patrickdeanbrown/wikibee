import runpy
import sys


def test_module_entrypoint_runs(monkeypatch, capsys):
    # Replace network call with a stub that returns predictable values
    def fake_extract(url, **kwargs):
        return ("Fake content.", "Fake Title")

    # Monkeypatch the extract function used by the CLI
    import wiki_extractor.cli as cli

    monkeypatch.setattr(cli, 'extract_wikipedia_text', fake_extract)

    # Provide args for the module so the CLI runs quickly and doesn't write files
    # Simulate: python -m wiki_extractor https://example.org/wiki/Fake
    monkeypatch.setattr(sys, 'argv', ['wiki_extractor', 'https://example.org/wiki/Fake'])

    # Running the module should not raise
    runpy.run_module('wiki_extractor', run_name='__main__')

    # capture output to ensure it wrote the success message
    captured = capsys.readouterr()
    assert 'Output saved to' in captured.out or 'Fake content.' in captured.out

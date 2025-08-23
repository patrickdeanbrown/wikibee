# wiki_extractor

[![CI](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml/badge.svg)](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml)

Small utility to extract plain text from Wikipedia articles and produce a TTS-friendly plain text file.

Requirements
- Python 3.8-3.13

Quickstart (PowerShell)

```powershell
# install
pip install wiki-extractor
# or
pipx install wiki-extractor

# extract an article and produce TTS file
wiki-extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file --heading-prefix "Section:" -o output
```

Usage

- CLI flags: `--article/-a` (required), `--yolo/-y`, `--output-dir`, `--filename`, `--no-save`, `--timeout`, `--lead-only`, `--tts-file`, `--heading-prefix`, `--verbose`.

**New Search Feature**: The tool now accepts both Wikipedia URLs and free-form search terms:

```powershell
# URL (traditional)
wiki-extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output

# Search term with fuzzy matching
wiki-extractor -a "homer ancient greek poet" --tts-file -o output

# Auto-select first result (--yolo)
wiki-extractor -a "homer poet" --yolo --tts-file -o output
```

Notes
- The TTS file strips Markdown markers (including `#`) so TTS engines like Kokoro won't say "number" for headings.
- Optional number-to-word conversion requires the `inflect` package.

Development
- Tests are under `tests/`. Run `pytest` in the project root inside the venv.

Run linters and tests (PowerShell)

```powershell
# run pre-commit hooks
.venv\Scripts\pre-commit run --all-files

# run tests
.venv\Scripts\pytest -q
```

Package entrypoint
------------------

After installation the `wiki-extractor` console script is available. You can also run the tool as a package module:

```powershell
# console script
wiki-extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output

# run via module
python -m wiki_extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output
```


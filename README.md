# wiki_extractor

[![CI](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml/badge.svg)](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml)

Small utility to extract plain text from Wikipedia articles and produce a TTS-friendly plain text file.

Requirements
- Python 3.8+
- See `requirements.txt` for runtime/dev dependencies.

Quickstart (PowerShell)

```powershell
# create and activate venv
python -m venv .venv
. .\.venv\Scripts\Activate.ps1

# install deps
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt

# extract an article and produce TTS file
.venv\Scripts\python extract.py "https://en.wikipedia.org/wiki/Homer" --tts-file --heading-prefix "Section:" -o output
```

Usage

- CLI flags: `--output-dir`, `--filename`, `--no-save`, `--timeout`, `--lead-only`, `--tts-file`, `--heading-prefix`, `--verbose`.

Notes
- The TTS file strips Markdown markers (including `#`) so TTS engines like Kokoro won't say "number" for headings.
- Optional number-to-word conversion requires the `inflect` package.

Development
- Tests are under `tests/`. Run `pytest` in the project root inside the venv.

Run linters and tests (PowerShell)

```powershell
# run ruff linter
.venv\Scripts\ruff check .

# run tests
.venv\Scripts\pytest -q
```

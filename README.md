# wiki_extractor

[![CI](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml/badge.svg)](https://github.com/patrickdeanbrown/wiki_extractor/actions/workflows/python-tests.yml)

Small utility to extract plain text from Wikipedia articles and produce a TTS-friendly plain text file.

Requirements
- Python 3.8-3.13
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
.venv\Scripts\python extract.py -a "https://en.wikipedia.org/wiki/Homer" --tts-file --heading-prefix "Section:" -o output
```

Usage

- CLI flags: `--article/-a` (required), `--yolo/-y`, `--output-dir`, `--filename`, `--no-save`, `--timeout`, `--lead-only`, `--tts-file`, `--heading-prefix`, `--verbose`.

**New Search Feature**: The tool now accepts both Wikipedia URLs and free-form search terms:

```powershell
# URL (traditional)
.venv\Scripts\python extract.py -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output

# Search term with fuzzy matching
.venv\Scripts\python extract.py -a "homer ancient greek poet" --tts-file -o output

# Auto-select first result (--yolo)
.venv\Scripts\python extract.py -a "homer poet" --yolo --tts-file -o output
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

You can run the tool as a package module as an alternative to the top-level script:

```powershell
# run via module
.venv\Scripts\python -m wiki_extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output
```

If you install the project in editable mode during development the `console_scripts` entrypoint will be available as `wiki-extractor`:

```powershell
# editable install
.venv\Scripts\python -m pip install -e .

# then run
wiki-extractor -a "https://en.wikipedia.org/wiki/Homer" --tts-file -o output
```

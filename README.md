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
wiki-extractor "Homer" --tts --heading-prefix "Section:" -o output
```

Usage

- CLI flags: `article` (positional), `--yolo/-y`, `--output/-o`, `--filename/-f`, `--no-save/-n`, `--timeout/-t`, `--lead-only/-l`, `--tts`, `--heading-prefix`, `--verbose/-v`.

**New Search Feature**: The tool now accepts both Wikipedia URLs and free-form search terms:

```powershell
# URL (traditional)
wiki-extractor "https://en.wikipedia.org/wiki/Homer" --tts -o output

# Search term with fuzzy matching
wiki-extractor "homer ancient greek poet" --tts -o output

# Auto-select first result (--yolo)
wiki-extractor "homer poet" --yolo --tts -o output
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
wiki-extractor "https://en.wikipedia.org/wiki/Homer" --tts -o output

# run via module
python -m wiki_extractor "https://en.wikipedia.org/wiki/Homer" --tts -o output
```

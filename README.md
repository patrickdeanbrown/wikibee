# wikibee

[![CI](https://github.com/patrickdeanbrown/wikibee/actions/workflows/python-tests.yml/badge.svg)](https://github.com/patrickdeanbrown/wikibee/actions/workflows/python-tests.yml)

Small utility to extract plain text from Wikipedia articles and produce a TTS-friendly plain text file.

Requirements
- Python 3.8-3.13

Quickstart (PowerShell)

```powershell
# install
pip install wikibee
# or
pipx install wikibee

# extract an article and produce TTS file
wikibee "Homer" --tts --heading-prefix "Section:" -o output
```

### One-step pipx install

The repository provides a small `Makefile` helper that installs the package
with [pipx](https://pipx.pypa.io/) and verifies the command is available:

```bash
make install
```

This checks that `pipx` is present, installs the project and runs
`wikibee --help` to confirm everything is wired up.

Usage

- CLI flags: `article` (positional), `--yolo/-y`, `--output/-o`, `--filename/-f`, `--no-save/-n`, `--timeout/-t`, `--lead-only/-l`, `--tts`, `--heading-prefix`, `--verbose/-v`.

**New Search Feature**: The tool now accepts both Wikipedia URLs and free-form search terms:

```powershell
# URL (traditional)
wikibee "https://en.wikipedia.org/wiki/Homer" --tts -o output

# Search term with fuzzy matching
wikibee "homer ancient greek poet" --tts -o output

# Auto-select first result (--yolo)
wikibee "homer poet" --yolo --tts -o output
```

Notes
- The TTS file strips Markdown markers (including `#`) so TTS engines like Kokoro won't say "number" for headings.
- Optional number-to-word conversion requires the `inflect` package.
- Rich-powered console messages provide clearer, colorized CLI output.

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

After installation the `wikibee` console script is available. You can also run the tool as a package module:

```powershell
# console script
wikibee "https://en.wikipedia.org/wiki/Homer" --tts -o output

# run via module
python -m wikibee "https://en.wikipedia.org/wiki/Homer" --tts -o output
```

### Standalone binaries

Release builds include standalone executables for Windows and
Linux created with PyInstaller. For macOS users, install via pipx:

```bash
pipx install wikibee
```

For Windows/Linux, download the binary for your platform from
the [releases page](https://github.com/patrickdeanbrown/wikibee/releases),
unzip it if needed, move `wikibee` into a directory on your `PATH`
(for example `/usr/local/bin`), make it executable if necessary
(`chmod +x wikibee` on Unix-like systems) and run it directly:

```bash
./wikibee "Homer" --tts --heading-prefix "Section:" -o output
```

These binaries bundle Python so no interpreter or virtual environment is
required.

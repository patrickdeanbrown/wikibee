# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a Python tool for extracting and processing Wikipedia articles into TTS-friendly formats. The project uses a modern Python packaging structure:

- **`wiki_extractor/`**: Main package containing the core functionality
  - `cli.py`: Main CLI logic and Wikipedia extraction functions
  - `client.py`: Wikipedia API client
  - `formatting.py`: Text processing and TTS formatting utilities
  - `tts_openai.py`: OpenAI-compatible TTS client for audio synthesis
- **`extract.py`**: Backward-compatible shim for legacy imports
- **`tests/`**: Comprehensive test suite
- **`scripts/`**: Development utilities

## Architecture

The application follows a layered architecture:

1. **CLI Layer** (`cli.py`): Argument parsing, orchestration, and file I/O
2. **Client Layer** (`client.py`): Wikipedia API interactions
3. **Processing Layer** (`formatting.py`): Text transformation and TTS optimization
4. **Audio Layer** (`tts_openai.py`): Optional TTS audio generation

The package exports a clean public API through `__init__.py` while maintaining backward compatibility with the original `extract.py` interface.

## Development Commands

Setup and installation:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install in editable mode (enables console script)
pip install -e .
```

Testing and linting:
```bash
# Run tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_extract.py

# Run linter
ruff check .

# Run linter with fixes
ruff check . --fix
```

## Usage Patterns

The tool can be used in multiple ways:

1. **Direct script**: `python extract.py -a [url_or_search] [options]`
2. **Module execution**: `python -m wiki_extractor -a [url_or_search] [options]`
3. **Console script**: `wiki-extractor -a [url_or_search] [options]` (after `pip install -e .`)
4. **Programmatic**: Import functions from `wiki_extractor` package

### New Search Feature

The tool now supports free-form search terms in addition to URLs:

- **URL input**: `wiki-extractor -a "https://en.wikipedia.org/wiki/Wars_of_the_Roses"`
- **Search input**: `wiki-extractor -a "war of the roses"`
- **Fuzzy search**: `wiki-extractor -a "war fo the rose"` (handles typos)
- **Auto-select**: `wiki-extractor -a "wars roses" --yolo` (picks first result)

The search feature provides:
- Interactive colored menu for multiple results
- Automatic selection for single results
- Fuzzy matching with typo tolerance via Wikipedia's OpenSearch API
- Graceful handling of no results

### UI Design Decisions

- **No emojis**: The interface uses ANSI colors instead of emojis for better readability and professionalism
- **Numbered menu**: Uses simple number selection (1-10) + Enter rather than arrow key navigation for cross-platform compatibility across all terminals (Windows Command Prompt, PowerShell, macOS Terminal, Linux terminals, CI/CD environments, SSH sessions)

Key CLI options: `--article/-a` (required), `--yolo/-y`, `--output-dir`, `--tts-file`, `--tts-audio`, `--heading-prefix`, `--lead-only`, `--verbose`

## Error Handling

The code uses structured exceptions:
- `NetworkError`: Request/network failures
- `APIError`: Invalid API responses
- `NotFoundError`: Missing pages/extracts
- `DisambiguationError`: Disambiguation pages
- `TTSClientError`: TTS synthesis failures

## Configuration

- **Ruff**: Line length 88 characters (strictly enforced), linting rules in `pyproject.toml`
- **Code style**: All lines must be ≤88 characters to pass linting
- **Pytest**: Configuration in `setup.cfg`
- **Console script**: `wiki-extractor` entry point defined in `setup.cfg`
- **TTS defaults**: Kokoro voice `af_sky+af_bella`, MP3 format, localhost:8880 server

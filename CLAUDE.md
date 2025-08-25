# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a Python tool for extracting and processing Wikipedia articles into TTS-friendly formats. The project uses a modern Python packaging structure:

- **`wikibee/`**: Main package containing the core functionality
  - `cli.py`: Main CLI logic and Wikipedia extraction functions
  - `client.py`: Wikipedia API client with retry logic and session management
  - `formatting.py`: Text processing and TTS formatting utilities
  - `tts_normalizer.py`: Advanced TTS text normalization (royal names, centuries, Latin abbreviations)
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
pip install -e .[dev]
```

Testing and linting:
```bash
# Run tests
pytest -q

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_extract.py

# Run smoke test
python scripts/smoke_extract.py

# Run linter
ruff check .

# Run linter with fixes
ruff check . --fix

# Install and run pre-commit hooks
pre-commit install
pre-commit run --all-files
```

## Usage Patterns

The tool can be used in multiple ways:

1. **Direct script**: `python extract.py [url_or_search] [options]`
2. **Module execution**: `python -m wikibee [url_or_search] [options]`
3. **Console script**: `wikibee [url_or_search] [options]` (after `pip install -e .`)
4. **Programmatic**: Import functions from `wikibee` package

### New Search Feature

The tool now supports free-form search terms in addition to URLs:

- **URL input**: `wikibee "https://en.wikipedia.org/wiki/Wars_of_the_Roses"`
- **Search input**: `wikibee "war of the roses"`
- **Fuzzy search**: `wikibee "war fo the rose"` (handles typos)
- **Auto-select**: `wikibee "wars roses" --yolo` (picks first result)

The search feature provides:
- Interactive colored menu for multiple results
- Automatic selection for single results
- Fuzzy matching with typo tolerance via Wikipedia's OpenSearch API
- Graceful handling of no results

### UI Design Decisions

- **No emojis**: The interface uses ANSI colors instead of emojis for better readability and professionalism
- **Numbered menu**: Uses simple number selection (1-10) + Enter rather than arrow key navigation for cross-platform compatibility across all terminals (Windows Command Prompt, PowerShell, macOS Terminal, Linux terminals, CI/CD environments, SSH sessions)

Key CLI options: `article` (positional), `--yolo/-y`, `--output/-o`, `--tts`, `--audio`, `--heading-prefix`, `--lead-only/-l`, `--verbose/-v`

## Error Handling

The code uses structured exceptions defined in `cli.py` and `tts_openai.py`:
- `NetworkError`: Request/network failures, timeouts, connection issues
- `APIError`: Invalid API responses from Wikipedia
- `NotFoundError`: Missing pages/extracts (404 responses)
- `DisambiguationError`: Disambiguation pages requiring user selection
- `TTSClientError`: TTS synthesis failures, server unavailable

### Exception Handling Patterns
```python
try:
    result = client.search_articles(search_term, timeout=args.timeout)
except requests.exceptions.RequestException as e:
    console.print(f"[red]Search failed: {e}[/]")
    return None
```

All exceptions inherit from `RuntimeError` and provide meaningful error messages for CLI output.

## Configuration

- **Ruff**: Line length 88 characters (strictly enforced), linting rules in `pyproject.toml`
- **Code style**: All lines must be ≤88 characters to pass linting
- **Pytest**: Configuration in `setup.cfg`
- **Console script**: `wikibee` entry point defined in `pyproject.toml`
- **TTS defaults**: Kokoro voice `af_sky+af_bella`, MP3 format, localhost:8880 server

## API Integration Patterns

### Wikipedia Client Usage
The `WikiClient` class provides robust Wikipedia API interaction:
```python
client = WikiClient()
# Search with retry logic and proper error handling
results = client.search_articles(search_term, limit=10, timeout=30)
# Extract article text with disambiguation handling
text = client.extract_article_text(article_url, timeout=30)
```

### TTS Integration
```python
# Text normalization for better TTS pronunciation
normalized_text = normalize_for_tts(raw_text)
# TTS client for audio synthesis
tts_client = TTSOpenAIClient(base_url="http://localhost:8880/v1", voice="af_sky+af_bella")
```

## Testing Strategy

### Test Categories
- **Unit tests**: Individual function testing (`test_extract.py`, `test_tts_normalizer.py`)
- **Integration tests**: API interaction testing (`test_search.py`, `test_tts_openai.py`)  
- **Package tests**: Import and entrypoint verification (`test_package_exports.py`, `test_entrypoint.py`)
- **Smoke tests**: End-to-end validation (`scripts/smoke_extract.py`)

### Mock Usage
Tests use `requests-mock` for Wikipedia API mocking:
```python
import requests_mock
@requests_mock.Mocker()
def test_search_articles(m):
    m.get(url, json=mock_response)
    # Test implementation
```

## Console Output Formatting

Uses Rich library for colored, structured CLI output:
- **Colors**: `[red]` errors, `[yellow]` warnings, `[green]` success, `[cyan]` info
- **Progress**: Search results numbered (1-10), clear selection prompts
- **Error display**: Structured error messages with troubleshooting hints

## Troubleshooting

### Common Issues
- **Import errors**: Ensure `pip install -e .[dev]` was run in activated virtual environment
- **Search failures**: Check internet connection; Wikipedia API may be temporarily unavailable
- **TTS errors**: Verify TTS server running on localhost:8880 (if using --audio flag)
- **File permission errors**: Check output directory write permissions

### Development Environment Issues
- **Pre-commit hook failures**: Run `pre-commit run --all-files` to fix formatting issues
- **Test failures**: Use `pytest -v` for detailed output; check mock setup for API tests

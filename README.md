# wikibee

[![CI](https://github.com/patrickdeanbrown/wikibee/actions/workflows/python-tests.yml/badge.svg)](https://github.com/patrickdeanbrown/wikibee/actions/workflows/python-tests.yml)
[![Type Checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue.svg)](CONTRIBUTING.md#type-safety--mypy-required)
[![Docs](https://img.shields.io/badge/docs-read-brightgreen.svg)](docs/README.md)
[![PyPI version](https://badge.fury.io/py/wikibee.svg)](https://badge.fury.io/py/wikibee)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Extract Wikipedia articles and convert them to TTS-friendly text and audio. Search by URL or keywords, get clean markdown and audio-optimized output.

## What is wikibee?

wikibee transforms Wikipedia articles into clean, accessible content perfect for:
- **Accessibility**: Convert text to speech for visually impaired users
- **Podcast creation**: Research and content preparation
- **Educational materials**: Clean text for study guides
- **Offline reading**: Save articles in markdown format
- **Audio content**: Generate TTS-ready text and audio files

## Quick Start

Install wikibee and create your first audio file in under 30 seconds:

```bash
# Install (recommended method)
pipx install wikibee

# Search and convert an article
wikibee "Albert Einstein" --tts --output my-audio/

# Or use a direct URL  
wikibee "https://en.wikipedia.org/wiki/Artificial_intelligence" --tts
```

That's it! You now have clean markdown and TTS-optimized text files ready for audio conversion.

### Audio Prerequisites

wikibee streams audio through an OpenAI-compatible endpoint. Start a local server
such as [kokoro](https://github.com/dtlnor/kokoro) on `http://localhost:8880/v1`
before running `--tts-audio`. Configure alternative hosts with the `--tts-server`
flag or via the generated `config.toml`.

## Installation

### Option 1: pipx (Recommended)
```bash
pipx install wikibee
```

### Option 2: pip
```bash
pip install wikibee
```

### Option 3: Standalone Binaries

**Windows/Linux**: Download from [releases](https://github.com/patrickdeanbrown/wikibee/releases)

**macOS**: Use pipx installation (binaries not provided for macOS)

### System Requirements
- Python 3.8 or higher
- Internet connection for Wikipedia access
- Optional: TTS server for audio generation

## Basic Usage

### Search by Keywords
```bash
# Simple search with fuzzy matching
wikibee "war of the roses"

# Auto-select first result (no interactive menu)
wikibee "napoleon bonaparte" --yolo

# Save to specific directory
wikibee "quantum computing" --output research/
```

### Use Direct URLs
```bash
# Process specific Wikipedia page
wikibee "https://en.wikipedia.org/wiki/Machine_learning"

# Get only the introduction section
wikibee "https://en.wikipedia.org/wiki/Python" --lead-only
```

### Generate Audio-Ready Content
```bash
# Create TTS-optimized text
wikibee "Ancient Rome" --tts

# Customize heading format for TTS
wikibee "World War II" --tts --heading-prefix "Section:"

# Specify output filename
wikibee "Mozart" --tts --output music/ --filename mozart_biography
```

### Generate Audio (Requires TTS Server)
```bash
# Generate audio using local TTS server
wikibee "Ancient Rome" --audio

# Generate M4B audiobook with chapters (from section headers)
wikibee "History of Rome" --audio --tts-format m4b

# Use a specific voice and normalize text for better pronunciation
wikibee "Quantum Mechanics" --audio --tts-voice "af_sky" --tts-normalize
```

### Configuration
```bash
# Initialize a default configuration file
wikibee config init

# The config file allows you to set default output directories, 
# TTS server URLs, voices, and more.
```

## Common Use Cases

### For Accessibility
```bash
# Create clean, readable text files
wikibee "Marie Curie" --tts --output biographies/
# Output: marie_curie.md and marie_curie.txt (TTS-ready)
```

### For Podcast Research
```bash
# Quick research with minimal processing
wikibee "blockchain technology" --lead-only --output research/
```

### For Educational Content
```bash
# Batch process multiple topics
wikibee "photosynthesis" --tts --output biology/
wikibee "mitosis" --tts --output biology/
wikibee "evolution" --tts --output biology/
```

## Key Features

- **Smart Search**: Fuzzy matching handles typos and partial queries
- **Interactive Selection**: Choose from multiple search results with a numbered menu
- **Clean Output**: Removes Wikipedia markup, leaving clean markdown
- **Audio Generation**: Generate MP3 or M4B audiobooks with chapter markers
- **TTS Optimization**: Strips formatting markers and normalizes text for better pronunciation
- **Flexible Output**: Save to custom directories with custom filenames
- **Error Handling**: Graceful handling of network issues and missing pages
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get up and running in 5 minutes
- **[Basic Usage Tutorial](docs/tutorial/basic-usage.md)** - Learn the fundamentals
- **[Python API Tutorial](docs/tutorial/api-usage.md)** - Programmatic access
- **[CLI Reference](docs/reference/cli-reference.md)** - All commands and options
- **[Configuration Guide](docs/reference/configuration.md)** - Settings and overrides
- **[Troubleshooting](docs/reference/troubleshooting.md)** - Common issues and solutions

## Development

wikibee is built with modern Python practices:

```bash
# Set up development environment
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest -q

# Check code style
ruff check .
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

Quick commands:

```bash
# Install dev dependencies
pip install -e .[dev]

# Run lint, typecheck, and tests via nox
nox

# Optional smoke test (manual; requires local TTS server)
python scripts/smoke_extract.py --skip-search --no-tts-audio
```

## Examples and Scripts

The `scripts/` directory contains working examples:
- `smoke_extract.py` - Basic extraction example
- See `docs/guides/examples.md` for more real-world scenarios

## Getting Help

- **Documentation**: Check the `docs/` directory for comprehensive guides
- **Issues**: [Report bugs or request features](https://github.com/patrickdeanbrown/wikibee/issues)
- **Discussions**: Ask questions in GitHub discussions

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Code style and testing requirements
- Submitting pull requests
- Reporting bugs and requesting features

---

**Made with care for the Wikipedia community and accessibility advocates everywhere.**

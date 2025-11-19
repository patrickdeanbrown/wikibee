# Changelog

All notable changes to wikibee will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite with tutorials and guides
- MIT license
- Contributor guidelines and code of conduct
- Complete API reference documentation

## [Unreleased]

## [0.1.2] - 2025-11-19

### Added
- **Audio Generation**: Support for generating MP3 and M4B audio files directly via CLI and API.
- **M4B Chapter Support**: Automatically converts Wikipedia section headers into M4B chapters for easy navigation.
- **Configuration Management**: New `config init` command to generate a default configuration file.
- **Text Normalization**: New `--tts-normalize` flag for advanced text processing (abbreviation expansion, spacing fixes).
- **Documentation**: Comprehensive updates to README, Quickstart, and Tutorials covering new audio features.

### Changed
- Updated `.gitignore` to exclude `.nox/` directory.
- Improved `README.md` with clearer feature highlights and audio generation examples.

### Fixed
- Documentation consistency across all guides.

### Added
- Complete project rebrand from wiki_extractor to wikibee
- Modern Python packaging with hatchling build backend
- PyPI distribution ready with proper metadata
- Search functionality with fuzzy matching support
- Interactive colored menu for search results
- TTS-friendly text processing with customizable options
- OpenAI-compatible TTS client integration
- Comprehensive test suite with high coverage
- GitHub Actions CI/CD pipeline
- Support for both URL and free-form search inputs

### Changed
- Package name from `wiki_extractor` to `wikibee`
- Console script from `wiki-extractor` to `wikibee`
- Build system from setuptools to hatchling
- Distribution strategy: macOS via pipx, Windows/Linux via binaries

### Removed
- macOS binary builds (use pipx installation instead)

### Technical Details
- Python 3.8+ support
- Modern type hints throughout codebase
- Structured exception handling
- Backward compatibility maintained via extract.py shim
- Rich-powered console output with colors
- Robust error handling and user feedback

## Pre-1.0 History

Previous versions were released as `wiki_extractor` and included basic Wikipedia extraction functionality, TTS processing, and CLI interface development.

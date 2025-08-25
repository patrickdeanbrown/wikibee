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

## [0.1.0] - 2024-12-XX

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

# Wikibee AGENTS.md

A comprehensive guide for AI agents working on the wikibee Wikipedia extraction tool.

## Dev environment tips

### Python Environment Setup
- **Python version**: Use Python 3.8+ (recommended: 3.12)
- **Package manager**: Use `uv` for faster dependency management:
  ```bash
  uv venv -p 3.12
  source .venv/bin/activate
  uv pip install -e ".[dev]"
  ```
- **Alternative with pip**:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # On Windows: .venv\Scripts\activate
  pip install --upgrade pip
  pip install -e .[dev]
  ```

### Pre-commit Setup
```bash
pre-commit install
pre-commit run --all-files
```

### Development Dependencies
The project includes these development tools:
- `pytest`: Testing framework
- `requests-mock`: HTTP request mocking
- `ruff`: Fast Python linter and formatter
- `pre-commit`: Git hooks for code quality

## Testing instructions

### Test Commands
```bash
# Run all tests quietly
pytest -q

# Run tests with verbose output and coverage
pytest -v

# Run specific test categories
pytest tests/test_extract.py          # Core extraction logic
pytest tests/test_search.py           # Search functionality  
pytest tests/test_tts_normalizer.py   # Text normalization
pytest tests/test_tts_openai.py       # TTS integration
pytest tests/test_package_exports.py  # Public API verification

# Run smoke test (end-to-end validation)
python scripts/smoke_extract.py

# Test console script installation
wikibee --help
```

### Test Patterns
- **Mock usage**: All tests use `requests-mock` for Wikipedia API calls
- **Error testing**: Each exception type has dedicated test cases
- **Integration testing**: Tests cover CLI, API client, and TTS functionality
- **Backward compatibility**: Tests verify legacy `extract.py` interface

### Coverage Expectations
- All public functions must have test coverage
- Error handling paths must be tested
- CLI argument parsing must be validated
- Mock all external API calls (Wikipedia, TTS server)

## Linting and formatting

### Code Quality Tools
```bash
# Run linter (check only)
ruff check .

# Run linter with automatic fixes
ruff check . --fix

# Check specific files
ruff check wikibee/cli.py tests/

# Pre-commit hooks (runs ruff, isort, black)
pre-commit run --all-files
```

### Code Style Requirements
- **Line length**: Strictly 88 characters (enforced by ruff)
- **Import sorting**: Handled by `isort` with black profile
- **Formatting**: Handled by `black` formatter
- **Type hints**: Required for all function parameters and returns
- **Docstrings**: Required for all public functions using Google style

## PR instructions

### Commit Message Format
Use conventional commit format:
```
type: description

feat: add search functionality for Wikipedia articles
fix: handle disambiguation pages correctly
docs: update CLI usage examples
refactor: extract TTS normalization to separate module
test: add coverage for error handling
```

### Pre-merge Checklist
- [ ] All tests pass: `pytest -q`
- [ ] Linting passes: `ruff check .`
- [ ] Pre-commit hooks pass: `pre-commit run --all-files`  
- [ ] Smoke test passes: `python scripts/smoke_extract.py`
- [ ] Type hints added for new functions
- [ ] Docstrings added for public functions
- [ ] Tests added for new functionality
- [ ] Backward compatibility maintained

### Code Review Guidelines
- **Architecture**: Follow layered architecture (CLI → Client → Processing → Output)
- **Error handling**: Use structured exceptions with meaningful messages
- **Testing**: Mock all external dependencies (Wikipedia API, TTS server)
- **Documentation**: Update relevant docs for user-facing changes
- **Performance**: Consider API rate limiting and retry logic

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` with new features/fixes
3. Run full test suite with coverage
4. Create release tag following semantic versioning
5. GitHub Actions handles binary builds and distribution

## Project-specific guidelines

### Wikipedia API Integration
- Always use `WikiClient` class for API calls
- Implement proper retry logic with exponential backoff
- Handle disambiguation pages gracefully
- Respect Wikipedia's API rate limits
- Mock all API calls in tests

### TTS Text Processing
- Use `TTSNormalizer` for pronunciation improvements
- Follow patterns in `tts_normalizer.py` for new normalization rules
- Test TTS improvements with actual audio output when possible
- Maintain backward compatibility with existing text processing

### CLI Design Principles
- Use numbered menu selection (not arrow keys) for cross-platform compatibility
- Provide colored output using Rich library color codes
- Include progress indicators for long operations
- Offer both interactive and automated modes (--yolo flag)
- Maintain clean separation between CLI and core functionality

### File I/O Patterns
- Use `pathlib` over `os.path` for file operations
- Sanitize filenames using `sanitize_filename()` function
- Support custom output directories with `--output` flag
- Handle file permission errors gracefully
- Provide clear error messages for I/O failures

### Backward Compatibility
- Maintain `extract.py` shim for legacy imports
- Keep public API stable in `wikibee/__init__.py`
- Test backward compatibility in `test_package_exports.py`
- Document any breaking changes in `CHANGELOG.md`

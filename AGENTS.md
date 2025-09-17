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
# Run lint, typecheck, and tests on default interpreter
nox

# Lint / pre-commit checks only
nox -s lint

# Type checking only
nox -s typecheck

# Run pytest suite for a specific interpreter
nox -s tests-3.8   # also tests-3.9 ... tests-3.13

# Run smoke test manually (not part of CI)
python scripts/smoke_extract.py --skip-search --no-tts-audio

# Test console script installation
wikibee --help
```

### Test Patterns
- **Service-first**: Unit tests target the `wikibee.services.*` helpers so CLI and smoke tests share the same code paths.
- **Mock usage**: Use `requests-mock` for Wikipedia calls and fake OpenAI clients for audio.
- **Error testing**: Each exception type has dedicated test cases.
- **Integration testing**: `tests/test_cli_integration.py` and `scripts/smoke_extract.py` exercise the Typer CLI end-to-end.
- **Backward compatibility**: `extract.py` shim remains for legacy imports.

### Coverage Expectations
- All public functions must have test coverage
- Error handling paths must be tested
- CLI/service layers validated through integration tests
- Mock all external API calls (Wikipedia, TTS server)

## Linting and formatting

### Code Quality Tools
```bash
# Run linter (check only)
ruff check .

# Run linter with automatic fixes
ruff check . --fix

# Run lint & typecheck via nox
nox -s lint typecheck
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
- [ ] All sessions pass: `nox`
- [ ] Linting passes: `nox -s lint`
- [ ] Type checking passes: `nox -s typecheck`
- [ ] Smoke test passes: `python scripts/smoke_extract.py --skip-search --no-tts-audio`
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
- Typer app lives in `wikibee/cli.py` and re-exports modular commands from `wikibee/commands/`.
- `wikibee.commands.extract` handles orchestration using shared services (search/output/tts).
- Numbered menu selection (no arrow keys) for cross-platform compatibility.
- Rich library colors for feedback, `--yolo` for automation, and smoke/integration tests validate flows.

### File I/O Patterns
- Use `OutputManager` (`wikibee.services.output`) for all filesystem writes.
- `sanitize_filename()` (re-exported from `commands.extract`) normalizes article titles.
- Support custom output directories with `--output` and config defaults.
- Handle file permission errors gracefully and respect directory boundaries.

### Backward Compatibility
- Maintain `extract.py` shim for legacy imports.
- Keep public API stable in `wikibee/__init__.py`.
- Integration tests ensure command re-exports (e.g., `_handle_search`) remain accessible.
- Document any breaking changes in `CHANGELOG.md`.

# CLAUDE.md

Guidelines for Claude Code when contributing to wikibee. Keep this document in
sync with the canonical references: `README.md`, `CONTRIBUTING.md`, and the
`docs/` tree.

## Project structure snapshot

- `wikibee/cli.py` – Typer entry point that wires up all commands
- `wikibee/commands/` – CLI subcommands (`extract`, `config`, etc.)
- `wikibee/services/` – Output/search/TTS helpers used by the CLI layer
- `wikibee/client.py` – Wikipedia API wrapper with retry-aware session
- `wikibee/formatting.py` & `tts_normalizer.py` – text post-processing utilities
- `wikibee/tts_openai.py` – OpenAI-compatible TTS client
- `extract.py` – shim that re-exports the public API for legacy imports
- `tests/`, `scripts/` – automated coverage plus smoke tooling

The runtime flows `commands → services → client/formatting`, and all public
helpers are re-exported through `wikibee/__init__.py`.

## Working expectations for Claude

1. **Environment** – create a virtualenv (uv or `python -m venv`), activate it,
   then `pip install -e .[dev]`. Pre-commit hooks should stay enabled.
2. **Quality gates** – run `nox -s lint`, `nox -s typecheck`, and `nox -s tests`
   before requesting review. Use `python scripts/smoke_extract.py
   --skip-search --no-tts-audio` for optional manual verification.
3. **APIs** – use `WikiClient.search_articles(...)` to obtain canonical URLs and
   pass them to `extract_wikipedia_text(url, ...)`. There is no direct
   search-term extraction helper.
4. **File safety** – rely on `OutputManager` or `write_text_file` so writes stay
   inside the configured output directory.
5. **Docs stay honest** – when functionality changes, update
   `docs/reference/cli-reference.md`, tutorials, and `CHANGELOG.md` so they only
   describe features that exist in the codebase.

## Quick checklist for Claude-authored changes

- [ ] `nox -s lint typecheck tests` passes locally
- [ ] New or modified functions include type hints and docstrings as required by
      the contributing guide
- [ ] Tests cover the change (mock Wikipedia/TTS traffic instead of hitting the
      network)
- [ ] CLI/config/docs updated when flags or behavior change
- [ ] Legacy shims (`extract.py`, `wikibee/__init__.py`) continue to export the
      public API

Following this lightweight guide keeps the Claude-specific instructions aligned
with the single source of truth in the repository.

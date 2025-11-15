# Wikibee AGENTS.md

Short guide for AI agents working in this repository. When in doubt, defer to
the canonical docs:

- `README.md` – product overview and usage
- `CONTRIBUTING.md` – contributor expectations
- `docs/` – tutorials, configuration, and troubleshooting

## Working in the repo

1. **Set up Python** (3.8+, prefer 3.12):
   ```bash
   uv venv --python 3.12 && source .venv/bin/activate
   uv pip install -e ".[dev]"
   ```
   (or use `python -m venv` + `pip install -e .[dev]`).

2. **Run quality gates** exactly as CI does:
   ```bash
   nox -s lint      # ruff/black/isort/mypy via pre-commit
   nox -s typecheck # mypy wikibee
   nox -s tests     # pytest across the supported matrix
   ```
   Optional manual smoke run: `python scripts/smoke_extract.py --skip-search --no-tts-audio`.

3. **Keep hooks enabled**: `pre-commit install` then `pre-commit run --all-files`
   before submitting large edits.

## Guardrails for automated edits

- Preserve the layered architecture (`commands` → `services` → `client`/`formatting`).
- Use `WikiClient.search_articles()` to discover URLs and
  `extract_wikipedia_text(url)` for article content—there is no direct
  search-term extractor.
- All filesystem writes must go through `OutputManager` helpers or
  `write_text_file` to retain safety checks.
- Mock external services (Wikipedia, OpenAI-compatible TTS endpoints) in tests.
- Update relevant docs (`docs/quickstart.md`, `docs/tutorial/*.md`, etc.) for any
  user-facing change.

## Lightweight checklist for PRs authored by agents

- [ ] `nox -s lint typecheck tests` succeeds locally
- [ ] New code is fully typed and covered by tests
- [ ] CLI/config changes reflected in `docs/reference/cli-reference.md`
- [ ] Docs and changelog entries match reality (no references to missing files)
- [ ] Backward compatibility maintained (`extract.py` shim, public exports)

Sticking to this abbreviated process keeps the agent-specific guidance in sync
with the canonical developer documentation.

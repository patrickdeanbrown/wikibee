# GEMINI.md

## Critical Rules
1. **Always use `.venv`**: All python commands must use the virtual environment (e.g., `.venv/bin/python`, `.venv/bin/pip`).
2. **Verify locally**: You MUST run `nox` locally and ensure it passes before pushing any PR.
   ```bash
   nox  # Runs lint, typecheck, and tests
   ```

## Development Workflow
1. **Setup**:
   - Check for existing `.venv` first.
   - If missing, create using `uv`:
     ```bash
     uv venv --python 3.12
     ```
   - Activate and install:
     ```bash
     source .venv/bin/activate
     uv pip install -e ".[dev]"
     ```
2. **Quality Checks**:
   - `nox -s lint`: Format and lint (ruff, black, isort)
   - `nox -s typecheck`: Static analysis (mypy)
   - `nox -s tests`: Run unit tests
3. **Architecture**:
   - `commands` → `services` → `client`/`formatting`
   - Use `WikiClient` for API calls.
   - Use `OutputManager` for file writes.

## PR Checklist
- [ ] `nox` passes locally
- [ ] Code is typed and tested
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

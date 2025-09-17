"""Project automation sessions."""

from __future__ import annotations

import nox

PY_VERSIONS = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]

nox.options.sessions = ["lint", "typecheck", "tests"]


@nox.session(python="3.11")
def lint(session: nox.Session) -> None:
    """Run pre-commit hooks (ruff/black/isort/mypy)."""

    session.install("pre-commit")
    session.install(".[dev]")
    session.run(
        "pre-commit",
        "run",
        "--show-diff-on-failure",
        "--color=always",
        "--all-files",
        external=True,
    )


@nox.session(python="3.11")
def typecheck(session: nox.Session) -> None:
    """Run mypy static type checks."""

    session.install(".[dev]")
    session.run("mypy", "wikibee")


@nox.session(python=PY_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the pytest suite on all supported Python versions."""

    session.install("pip", "-U", "pip")
    session.install(".[dev]")
    session.run("python", "wikibee/__main__.py", "--help")
    session.run("pytest", "-q")

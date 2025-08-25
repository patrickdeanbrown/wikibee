"""Module entrypoint for `python -m wikibee`.

Delegates to the CLI app function for command-line execution.
"""

from __future__ import annotations

from wikibee import cli as _cli


def _main() -> None:
    _cli.app()


if __name__ == "__main__":
    _main()

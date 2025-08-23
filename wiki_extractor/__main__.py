"""Module entrypoint for `python -m wiki_extractor`.

Delegates to the `main()` function defined in the top-level `extract.py`
for compatibility with the existing tests and scripts.
"""

from __future__ import annotations

from . import cli as _cli


def _main() -> None:
    _cli.app()


if __name__ == "__main__":
    _main()

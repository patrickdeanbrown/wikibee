from __future__ import annotations

from typing import List, Optional, Tuple

import click
import typer
from rich.console import Console
from typer.core import TyperGroup

from . import config as config_cmd
from . import extract as extract_cmd

console = Console()


class _DefaultGroup(TyperGroup):
    """Click Group that treats non-command first argument as default command."""

    default_command_name = "extract"

    def resolve_command(
        self, ctx: click.Context, args: List[str]
    ) -> Tuple[Optional[str], Optional[click.Command], List[str]]:
        if (
            args
            and args[0] not in self.commands
            and self.default_command_name in self.commands
        ):
            args = [self.default_command_name] + args
        return super().resolve_command(ctx, args)


app = typer.Typer(cls=_DefaultGroup, no_args_is_help=True)

# Register commands
extract_cmd.register_extract(app)
config_cmd.register_config(app)

__all__ = ["app", "console"]

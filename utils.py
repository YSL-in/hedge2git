import sys
import typing as t

import click


def exit_with_error(msg: str) -> t.NoReturn:
    click.UsageError(msg, click.get_current_context()).show(sys.stderr)
    exit(1)

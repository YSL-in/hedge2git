import sys
import typing as t

import click

from hedgedoc import hedgedoc


def validate(**actions: t.Mapping) -> None:
    def exit_with_error(msg: str) -> t.NoReturn:
        click.UsageError(msg, click.get_current_context()).show(sys.stderr)
        exit(1)

    if actions['pull'] is not None and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")
    pass


def pull(branch: str) -> None:
    """It should be called each time
    TODO:
    - create the temp repo if not exists
    - pull the latest changes
    - checkout to an orphan branch
        - remove .git/index
        - clear all files
    - extract the notes from hedgedoc database
    - merge the orphan (--allow-unrelated-history --ff-only)
        - prompt to continue to solve conflict if any
    """
    if branch is None:
        return


def push(comment: str, flatten: bool) -> None:
    """
    TODO:
    - create the temp repo if not exists
    - pull the latest changes
    - extract the notes from hedgedoc database
    - add changes to working tree where hierarchy is optionally built according to tags (order matters!)
    - commit changes with an optional message
    - push changes
    """
    if comment is None:
        return

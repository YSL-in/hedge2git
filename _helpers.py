import sys
import typing as t
from functools import reduce
from pathlib import Path

import click
from sqlalchemy import Column

from configs import configs
from hedgedoc.core import hedgedoc


def validate(**actions: t.Mapping) -> None:
    def exit_with_error(msg: str) -> t.NoReturn:
        click.UsageError(msg, click.get_current_context()).show(sys.stderr)
        exit(1)

    if actions['pull'] is not None and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")
    pass


def pull(branch: str | None) -> None:
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


def push(comment: str | None, flatten: bool) -> None:
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

    sync_path = configs['SYNC_PATH']
    for note in hedgedoc.get_notes():
        path = reduce(lambda p, part: p / part, note.tags, sync_path)
        _write_file(path, note.content)


def _write_file(path: Path, content: str | Column[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content))

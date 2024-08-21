import re
import typing as t
from functools import reduce
from pathlib import Path

from sqlalchemy import Column

from configs import configs
from hedgedoc.core import hedgedoc_store
from utils import exit_with_error


def validate(**actions: t.Mapping) -> None:
    if actions['pull'] is not None and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")


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


def push(comment: str | None) -> None:
    """
    TODO:
    - create the temp repo if not exists
    - pull the latest changes
    - extract the notes from hedgedoc database
    - add changes to working tree where hierarchy is built according to tags
    - commit changes with an optional message
    - push changes
    """
    if comment is None:
        return

    sync_path = configs['SYNC_PATH']
    for note in hedgedoc_store.get_notes(owner=hedgedoc_store.get_current_user()):
        if not note.content:  # type: ignore
            continue

        # TODO: add confliction avoidance
        path = reduce(lambda p, part: p / part, note.tags, sync_path)
        name = note.title or re.split(r'\s', note.content, maxsplit=1)[0]  # type: ignore
        _write_file(path / f'{name}.md', note.content)


def _write_file(path: Path, content: str | Column[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content))

import re
import typing as t
from functools import reduce
from pathlib import Path

import git
import git.types
from sqlalchemy import Column

from configs import configs
from git_helper import git_helper
from hedgedoc import hedgedoc, hedgedoc_store
from hedgedoc.models import Note
from utils import exit_with_error


def validate(**actions: t.Mapping) -> None:
    if actions['pull'] is not None and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")


def pull(branch: str | None) -> None:
    """It should be called each time
    TODO:
    v pull the latest changes from the Git repository
    - traverse the hierarchy built according to the tags
    - compare against the notes extracted from the Hedgedoc
        - if GIT_NOTE[i] > HEDGEDOC_NOTE[j]:
            # TODO: either
            # - add append mode that keeps HEDGEDOC_NOTE[j++] and make force mode default
            # - add force mode that deletes HEDGEDOC_NOTE[j++] and make append mode default
        - if GIT_NOTE[i] < HEDGEDOC_NOTE[j]: add GIT_NOTE[i++] to HEDGEDOC
        - if GIT_NOTE[i] == HEDGEDOC_NOTE[j]: i++; j++;
    """
    if branch is None:
        return

    git_helper.pull()


def push(comment: str | None) -> None:
    """Apply changes from Hedgedoc to the Git repository."""
    if comment is None:
        return

    git_helper.pull()

    notes = []
    for note in hedgedoc_store.get_notes(owner=hedgedoc_store.get_current_user()):
        if not note.content:  # type: ignore
            continue

        # TODO: add confliction avoidance
        prefix_path = git_helper.repo_path
        base_path = reduce(lambda p, part: p / part, note.tags, Path())
        abs_path = prefix_path / base_path
        name = note.title or re.split(r'\s', note.content, maxsplit=1)[0]  # type: ignore
        notes.append(base_path / f'{name}.md')
        _write_file(abs_path, note.content)

    # TODO: add dry-run mode & show dirty files before committing
    git_helper.push(comment, notes)


def _write_file(path: Path, content: str | Column[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content))

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
    v create the temp repo if not exists
    v pull the latest changes
    - checkout to an orphan branch
        - remove .git/index
        - clear all files
    - extract the notes from hedgedoc database
    - merge the orphan (--allow-unrelated-history --ff-only)
        - prompt to continue to solve conflict if any
    - update the hedgedoc database with the latest notes
        - add new notes to browsing history
    """
    if branch is None:
        return

    sync_path = configs['LOCAL_REPO']
    repo = git.Repo.init(sync_path)
    origin = repo.create_remote('origin', configs['GIT_REPO'])
    try:
        origin.fetch()
    except git.GitCommandError:
        exit_with_error(f"Invalid git repository: {configs['GIT_REPO']}")
    origin.pull()

    print(f'{hedgedoc.get_history() = }')
    note: Note = hedgedoc_store.session.query(Note).filter(Note.id == '9d2ed746-5fe1-48c3-8e2f-1c683b6e9bb9').first()
    hedgedoc.add_history(note)


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

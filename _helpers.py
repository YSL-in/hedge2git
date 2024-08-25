import re
import typing as t
from functools import reduce
from pathlib import Path

import git
import git.types
from sqlalchemy import Column

from configs import configs
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

    print(f'{hedgedoc.get_history() = }')
    note: Note = hedgedoc_store.session.query(Note).filter(Note.id == '9d2ed746-5fe1-48c3-8e2f-1c683b6e9bb9').first()
    hedgedoc.add_history(note)


def push(comment: str | None) -> None:
    """
    TODO:
    v create the temp repo if not exists
    v pull the latest changes
    v extract the notes from hedgedoc database
    v add changes to working tree where hierarchy is built according to tags
    v commit changes with an optional message
    v push changes
    """
    if comment is None:
        return

    sync_path = configs['SYNC_PATH']
    repo = git.Repo.init(sync_path)
    origin = repo.create_remote('origin', configs['GIT_REPO'])
    try:
        origin.fetch()
    except git.GitCommandError:
        exit_with_error(f"Invalid git repository: {configs['GIT_REPO']}")
    origin.pull()

    notes = []
    for note in hedgedoc_store.get_notes(owner=hedgedoc_store.get_current_user()):
        if not note.content:  # type: ignore
            continue

        # TODO: add confliction avoidance
        path = reduce(lambda p, part: p / part, note.tags, sync_path)
        name = note.title or re.split(r'\s', note.content, maxsplit=1)[0]  # type: ignore
        notes.append(path / f'{name}.md')
        _write_file(notes[-1], note.content)

    # TODO: add dry-run mode & show dirty files before committing
    # TODO: create primary branch if none exists
    author = git.Actor(configs['GIT_USER'], configs['GIT_EMAIL'])
    repo.index.add(notes)
    repo.index.commit(comment, author=author, committer=author)
    origin.push().raise_if_error()


def _write_file(path: Path, content: str | Column[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content))

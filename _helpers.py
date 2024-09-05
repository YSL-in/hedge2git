import json
import os.path
from pathlib import Path

from sqlalchemy import Column

from git_helper import git_helper
from hedgedoc import Note, erase_notes, hedgedoc, write_notes
from utils import exit_with_error


def validate(**actions: str | bool | None) -> None:
    resp = hedgedoc.GET('me')
    status = json.loads(resp.text)['status']
    if status == 'forbidden':
        exit_with_error('Invalid email or password')

    if actions['pull'] and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")


def pull(pull_type: str, dry_run: bool) -> None:
    """Update Hedgedoc notes from the Git repository."""
    git_helper.pull()

    git_notes = []
    for path in git_helper.repo_path.rglob('*.md'):
        git_notes.append(path)
    git_notes.sort()

    def gen_path(note: Note):
        return git_helper.repo_path / os.path.sep.join(note.tags) / f'{note.title}.md'

    hedgedoc_notes = []
    for note in hedgedoc.get_notes(owner=hedgedoc.get_current_user()):
        hedgedoc_notes.append(note)
    hedgedoc_notes.sort(key=lambda note: gen_path(note))

    i = j = 0
    new_notes: list[Path] = []
    deprecated_notes: list[Note] = []
    while i < len(git_notes) and j < len(hedgedoc_notes):
        hedgedoc_note = gen_path(hedgedoc_notes[j])
        if git_notes[i] < hedgedoc_note:
            new_notes.append(git_notes[i])
            i += 1
        elif git_notes[i] > hedgedoc_note:
            deprecated_notes.append(hedgedoc_notes[j])
            j += 1
        else:
            i += 1
            j += 1

    while i < len(git_notes):
        new_notes.append(git_notes[i])
        i += 1

    while j < len(hedgedoc_notes):
        deprecated_notes.append(hedgedoc_notes[j])
        j += 1

    write_notes(new_notes, dry_run)
    if pull_type == 'overwrite':
        erase_notes(deprecated_notes, dry_run)


def push(comment: str | None, dry_run: bool) -> None:
    """Apply changes from Hedgedoc to the Git repository."""
    if comment is None:
        return

    git_helper.pull()

    notes = []
    for note in hedgedoc.get_notes(owner=hedgedoc.get_current_user()):
        if not note.title or not note.content:  # type: ignore
            continue

        # TODO: add confliction avoidance
        base_path = Path(os.path.sep.join(note.tags)) / f'{note.title}.md'
        abs_path = git_helper.repo_path / base_path
        notes.append(base_path)
        _write_file(abs_path, note.content)

    # TODO: add dry-run mode & show dirty files before committing
    git_helper.push(comment, notes, force=True)


def _write_file(path: Path, content: str | Column[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(str(content), encoding='utf-8')

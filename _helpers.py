import json
import os.path
from pathlib import Path

from git_helper import git_helper
from hedgedoc import Note, create_notes, delete_notes, hedgedoc
from utils import exit_with_error


def validate(**actions: str | bool | None) -> None:
    resp = hedgedoc.GET('me')
    status = json.loads(resp.text)['status']
    if status == 'forbidden':
        exit_with_error('Invalid email or password')

    if actions['pull'] and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")


def pull(*, overwrite: bool, dry_run: bool) -> None:
    """Update Hedgedoc notes from the Git repository."""
    git_helper.pull()

    # fetch remote notes
    git_notes = []
    for path in git_helper.repo_path.rglob('*.md'):
        git_notes.append(path)
    git_notes.sort()

    def gen_path(note: Note):
        return git_helper.repo_path / os.path.sep.join(note.tags) / f'{note.title}.md'

    # collect local notes (without writing them)
    hedgedoc_notes = []
    for note in hedgedoc.get_notes(owner=hedgedoc.get_current_user()):
        hedgedoc_notes.append(note)
    hedgedoc_notes.sort(key=lambda note: gen_path(note))

    # compare notes
    i = j = 0
    new_notes: list[Path] = []  # notes to be created in the database
    deprecated_notes: list[Note] = []  # notes to be deleted in the database
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

    # sync notes
    create_notes(new_notes, dry_run)
    if overwrite:
        delete_notes(deprecated_notes, dry_run)
    else:
        hedgedoc.refresh_alias(deprecated_notes, dry_run)


def push(comment: str, *, overwrite: bool, dry_run: bool) -> None:
    """Apply changes from Hedgedoc to the Git repository."""
    git_helper.pull()
    hedgedoc.refresh_alias(dry_run=dry_run)

    # fetch remote notes
    git_notes = []
    for path in git_helper.repo_path.rglob('*.md'):
        rel_path = path.relative_to(git_helper.repo_path)
        git_notes.append(rel_path)
    git_notes.sort()

    # collect local notes (without writing them)
    def gen_rel_path(note: Note):
        return Path(os.path.sep.join(note.tags)) / f'{note.title}.md'

    local_notes = []
    for note in hedgedoc.get_notes(owner=hedgedoc.get_current_user()):
        if not note.title or not note.content:  # type: ignore
            continue
        local_notes.append(note)
    local_notes.sort(key=gen_rel_path)

    # compare notes
    i = j = 0
    new_notes: list[Note] = []  # notes to be uploaded to the remote
    deprecated_notes: list[Path] = []  # notes to be removed from the remote
    while i < len(git_notes) and j < len(local_notes):
        local_note = gen_rel_path(local_notes[j])
        if git_notes[i] < local_note:
            deprecated_notes.append(git_notes[i])
            i += 1
        elif git_notes[i] > local_note:
            new_notes.append(local_notes[j])
            j += 1
        else:
            i += 1
            j += 1

    while i < len(git_notes):
        deprecated_notes.append(git_notes[i])
        i += 1

    while j < len(local_notes):
        new_notes.append(local_notes[j])
        j += 1

    # sync notes
    print('Uploading notes...')
    for note in new_notes:
        alias = Note.get_alias(content=note.content)  # type: ignore
        print(f'\t{note.title} ({alias})')
        if not dry_run:
            path = git_helper.repo_path / gen_rel_path(note)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(note.content), encoding='utf-8')

    if overwrite:
        print('Removing notes remotely...')
        for rel_path in deprecated_notes:
            path = git_helper.repo_path / rel_path
            alias = Note.get_alias(content=path.read_text())
            print(f'\t{path.stem} ({alias})')
            if not dry_run:
                path.unlink()

    if not dry_run:
        notes = list(str(path) for path in [*map(gen_rel_path, new_notes), *deprecated_notes])
        git_helper.push(comment, notes, force=True)

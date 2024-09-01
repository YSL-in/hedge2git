import os.path
from pathlib import Path

from sqlalchemy import Column

from git_helper import git_helper
from hedgedoc import hedgedoc, hedgedoc_store
from utils import exit_with_error


def validate(**actions: str) -> None:
    if actions['pull'] is not None and actions['push'] is not None:
        exit_with_error("Got both 'pull' and 'push'")


def pull(pull_type: str) -> None:
    """Update Hedgedoc notes from the Git repository."""
    # TODO: add pull_type=replace
    git_helper.pull()

    git_notes = []
    for path in git_helper.repo_path.rglob('*.md'):
        git_notes.append(path.relative_to(git_helper.repo_path))

    hedgedoc_notes = []
    for note in hedgedoc_store.get_notes(owner=hedgedoc_store.get_current_user()):
        hedgedoc_notes.append(Path('/'.join(note.tags)) / note.title)

    i = j = 0
    new_notes = []
    deprecated_notes = []
    while i < len(git_notes) and j < len(git_notes):
        if git_notes[i] < hedgedoc_notes[j]:
            new_notes.append(git_notes[i])
            i += 1
        elif git_notes[i] > hedgedoc_notes[j]:
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

    hedgedoc.write_notes(new_notes)
    hedgedoc.erase_notes(deprecated_notes)


def push(comment: str | None) -> None:
    """Apply changes from Hedgedoc to the Git repository."""
    if comment is None:
        return

    git_helper.pull()

    notes = []
    for note in hedgedoc_store.get_notes(owner=hedgedoc_store.get_current_user()):
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

import pathlib

from .core import hedgedoc
from .models import Note


def create_notes(paths: list[pathlib.Path], dry_run: bool) -> None:
    """Create Hedgedoc notes for a given list of Markdown files."""
    print('Creating notes...')
    for path in paths:
        content = path.read_text(encoding='utf-8')
        alias = Note.get_alias(title=path.stem, content=content)
        print(f'\t{path.stem} ({alias})')
        if not dry_run:
            hedgedoc.add_note(title=path.stem, content=content, alias=alias)

    if not dry_run:
        hedgedoc.refresh_history()


def delete_notes(notes: list[Note], dry_run: bool) -> None:
    """Delete Hedgedoc notes from the database."""
    print('Deleting notes...')
    for note in notes:
        print(f'\t{note.title} ({note.alias})')
        if not dry_run:
            hedgedoc.session.delete(note)

    if not dry_run:
        hedgedoc.refresh_history()

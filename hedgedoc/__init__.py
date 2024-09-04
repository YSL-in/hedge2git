import pathlib
import re

from .core import hedgedoc


def write_notes(paths: list[pathlib.Path]) -> None:
    """Create Hedgedoc notes for a given list of Markdown files."""
    for path in paths:
        content = path.read_text(encoding='utf-8')
        alias = _get_sanitized_alias(path.name)
        hedgedoc.add_note(content=content, alias=alias)

    current_user = hedgedoc.get_current_user()
    hedgedoc.refresh_history(new_notes=hedgedoc.get_notes(owner=current_user))


def erase_notes(paths: list[pathlib.Path]) -> None:
    for path in paths:
        alias = _get_sanitized_alias(path.name)
        hedgedoc.delete_note(alias)

    hedgedoc.refresh_history(new_notes=None)


def _get_sanitized_alias(fname: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', fname).lower()


def get_tags(content: str) -> list[str]:
    """Extract tags from a Markdown content."""
    tags = []
    template = r'`([^`]*)`'
    for line in content.split('\n'):
        if raw_tags := line.partition('###### tags')[-1]:
            tags += [tag for tag in re.findall(template, raw_tags) if tag]
    return tags

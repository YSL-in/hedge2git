import pytest

from .models import Note


@pytest.mark.parametrize(
    'content, expected_tags',
    (
        (
            '\n'.join([
                '###### tags: `tag1`, `tag2`',
                '###### tags: `tag2`, `tag3`',
            ]),
            ['tag1', 'tag2', 'tag3'],
        ),
        (
            '\n'.join([
                '---             ',
                'tags: tag1, tag2',
                '---             ',
            ]),
            ['tag1', 'tag2'],
        ),
        (
            '\n'.join([
                '--------',
                'tags:   ',
                '  - tag3',
                '  - tag4',
                '--------',
            ]),
            ['tag3', 'tag4'],
        ),
    ),
)
def test_get_tags(content, expected_tags) -> None:
    assert Note.get_tags(content) == expected_tags

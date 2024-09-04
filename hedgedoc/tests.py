import pytest

from . import get_tags


@pytest.mark.parametrize(
    'content, expected_tags',
    ((
        '\n'.join([
            '###### tags: `tag1`, `tag2`',
            '###### tags: `tag3`, `tag4`',
        ]),
        ['tag1', 'tag2', 'tag3', 'tag4'],
    ),),
)
def test_get_tags(content, expected_tags) -> None:
    assert get_tags(content) == expected_tags

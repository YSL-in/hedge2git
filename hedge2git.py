import typing as t
from datetime import datetime

import click

import _helpers


@click.command()
@click.option(
    '--pull', '--download', 'pull', metavar='BRANCH', type=str,
    is_flag=False, flag_value='main',  # TODO: make it configurable
    default=None, show_default=False,
    help='Pull the latest changes.',
)
@click.option(
    '--push', '--upload', 'push', metavar='COMMENT',
    is_flag=False, flag_value=datetime.now().strftime('Pushed at %Y-%m-%d %H:%M:%S'),
    default=None, show_default=True,
    help='Push changes.',
)
def hedge2git(**actions: t.Mapping):
    """
    Sync hedgedoc via Git registries. Use .env to configure repository, access token, etc.
    """
    _helpers.validate(**actions)

    if (branch := actions['pull']) is not None:
        _helpers.pull(branch)  # type: ignore

    if (comment := actions['push']) is not None:
        _helpers.push(comment)  # type: ignore


if __name__ == '__main__':
    hedge2git()

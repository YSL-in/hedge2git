from datetime import datetime

import click

import _helpers


@click.command()
@click.option(
    '--pull', '--download', 'pull',
    is_flag=True, default=False, show_default=True,
    help='Fetch and merge the latest changes.',
)
@click.option(
    '--pull-type', '--download-type', metavar='TYPE',
    type=click.Choice(['append', 'overwrite'], case_sensitive=False),
    default='append', show_default=True,
    help='Choose the pulling type: append, overwrite.',
)
@click.option(
    '--push', '--upload', 'push', metavar='COMMENT',
    is_flag=False, flag_value=datetime.now().strftime('Pushed at %Y-%m-%d %H:%M:%S'),
    default=None, show_default=True,
    help='Push changes.',
)
def hedge2git(**actions: str):
    """
    Sync hedgedoc via Git registries. Use .env to configure repository, access token, etc.
    """
    _helpers.validate(**actions)

    if actions['pull']:
        _helpers.pull(actions['pull_type'])

    if (comment := actions['push']) is not None:
        _helpers.push(comment)  # type: ignore


if __name__ == '__main__':
    hedge2git()

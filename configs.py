import shutil
from pathlib import Path

from dotenv import dotenv_values

configs: dict[str, any] = dotenv_values()  # type: ignore

if not configs['HEDGEDOC_SERVER'].endswith('/'):
    configs['HEDGEDOC_SERVER'] += '/'

configs['LOCAL_REPO'] = sync_path = Path('/tmp/hedge2git')  # noqa: S108
if sync_path.exists():
    bak_path = sync_path.with_suffix('.bak')
    if bak_path.exists():
        shutil.rmtree(bak_path)

    shutil.move(sync_path, bak_path)
    sync_path.mkdir()

configs['NOTE__IGNORED_TAGS'] = configs['NOTE__IGNORED_TAGS'].split(',')

import json
import pathlib
import re
import typing as t
from datetime import datetime
from urllib.parse import urlencode

import httpx
from parse import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs import configs
from utils import exit_with_error

from .models import Note, User


class HedgedocStore:
    def __init__(self) -> None:
        db_type = configs['DB_TYPE']
        db_user = configs['DB_USER']
        db_pass = configs['DB_PASS']
        db_host = configs['DB_HOST']
        db_port = configs['DB_PORT']
        db_name = configs['DB_NAME']
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}', future=True)
        self.session = sessionmaker(bind=engine)()

    def get_note(self, alias: str) -> Note:
        return self.session.query(Note).filter(Note.alias == alias).first()  # type: ignore

    def delete_note(self, alias: str) -> None:
        n_deleted = self.session.query(Note).filter(Note.alias == alias).delete()  # type: ignore
        if not n_deleted:
            print(f'warning: Note not found: {alias}')

    def get_notes(self, owner: User | None = None) -> list[Note]:
        if owner is None:
            return self.session.query(Note).all()
        return self.session.query(Note).filter(Note.owner_id == owner.id).all()

    def get_users(self) -> list[User]:
        return self.session.query(User).all()

    def get_current_user(self) -> User:
        if configs['USER_EMAIL'] is None:
            exit_with_error('USER_EMAIL is not set')
        return self.session.query(User).filter(User.email == configs['USER_EMAIL']).first()  # type: ignore


class HedgedocAPI:
    def __init__(self) -> None:
        self.server = httpx.URL(configs['HEDGEDOC_SERVER'])
        self.client = httpx.Client()
        self.client.post(self.server.join('login'), data={
            'email': configs['USER_EMAIL'],
            'password': configs['USER_PASSWORD'],
        })

        resp = self.client.get(self.server.join('me'))
        status = json.loads(resp.text)['status']
        if status == 'forbidden':
            exit_with_error('Invalid USER_EMAIL or USER_PASSWORD')

    def get_ref_id(self, note: Note) -> str:
        """Return the URL-referenced ID given a Note.short_id or Note.alias."""
        return parse(f'{self.server}{{}}', self.GET(note.short_id).headers['location'])[0]  # type: ignore

    def add_note(self, content: str, alias: str) -> None:
        # if not content:
        #     resp = self.GET('new')
        # elif not alias:
        #     resp = self.POST('new', content=content, content_type='text/markdown')
        resp = self.POST(f'new/{alias}', content=content, content_type='text/markdown')
        resp.raise_for_status()

    def get_history(self) -> list[dict[str, t.Any]]:
        return self.GET('history').json()['history']

    def refresh_history(self, new_notes: list[Note] | None = None) -> None:
        if new_notes:
            history = self.get_history()
            history += [
                {
                    'id': self.get_ref_id(note),
                    'text': note.title,
                    'time': int(datetime.now().timestamp()),
                    'tags': note.tags,
                }
                for note in new_notes
            ]
        else:
            history = [
                {
                    'id': self.get_ref_id(note),
                    'text': note.title,
                    'time': int(datetime.now().timestamp()),
                    'tags': note.tags,
                }
                for note in hedgedoc_store.get_notes()
            ]
        resp = self.POST(
            'history',
            content=urlencode({'history': json.dumps(history)}),
            content_type='application/x-www-form-urlencoded',
        )
        resp.raise_for_status()

    def GET(self, api: str) -> httpx.Response:
        return self.client.get(self.server.join(api))

    def POST(self, api: str, content: str, content_type: str) -> httpx.Response:
        return self.client.post(
            self.server.join(api),
            content=content,
            headers={'Content-Type': content_type},
        )


class Hedgedoc:
    def __init__(self) -> None:
        pass

    def write_notes(self, paths: list[pathlib.Path]) -> None:
        """Create Hedgedoc notes for a given list of Markdown files."""
        for path in paths:
            content = path.read_text(encoding='utf-8')
            alias = self._get_sanitized_alias(path.name)
            hedgedoc_api.add_note(content=content, alias=alias)

        current_user = hedgedoc_store.get_current_user()
        hedgedoc_api.refresh_history(new_notes=hedgedoc_store.get_notes(owner=current_user))

    def erase_notes(self, paths: list[pathlib.Path]) -> None:
        for path in paths:
            alias = self._get_sanitized_alias(path.name)
            hedgedoc_store.delete_note(alias)

        hedgedoc_api.refresh_history(new_notes=None)

    def _get_sanitized_alias(self, fname: str) -> str:
        return re.sub(r'[^a-zA-Z0-9]+', '-', fname).lower()


hedgedoc_store = HedgedocStore()
hedgedoc_api = HedgedocAPI()
hedgedoc = Hedgedoc()

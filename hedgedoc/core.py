import json
import typing as t
import uuid
from datetime import datetime
from urllib.parse import urlencode

import httpx
from parse import parse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from configs import configs
from utils import exit_with_error

from .models import Note, T_Base, User


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

    def get_or_create(self, model: type[T_Base], defaults: dict = {}, **kwargs) -> tuple[T_Base, bool]:
        obj = self.session.query(model).filter_by(**kwargs).first()
        if obj:
            return obj, False

        obj = model(**kwargs, **defaults)
        self.session.add(obj)
        self.session.commit()
        return obj, True


class HedgedocAPI:
    def __init__(self) -> None:
        self.server = httpx.URL(configs['HEDGEDOC_SERVER'])
        self.client = httpx.Client()
        self.client.post(self.server.join('login'), data={
            'email': configs['HEDGEDOC_USER_EMAIL'],
            'password': configs['HEDGEDOC_USER_PASSWORD'],
        })

    def GET(self, api: str) -> httpx.Response:
        return self.client.get(self.server.join(api))

    def POST(self, api: str, content: str, content_type: str) -> httpx.Response:
        return self.client.post(
            self.server.join(api),
            content=content,
            headers={'Content-Type': content_type},
        )


class Hedgedoc(HedgedocAPI, HedgedocStore):
    def __init__(self) -> None:
        HedgedocAPI.__init__(self)
        HedgedocStore.__init__(self)

    # operations for Hedgedoc notes
    def get_notes(self, owner: User | None = None) -> list[Note]:
        """Return a list of notes for a given user which default to the current logged-in user."""
        if owner is None:
            return self.session.query(Note).all()
        return self.session.query(Note).filter(Note.owner_id == owner.id).all()

    def get_note(self, alias: str) -> Note:
        return self.session.query(Note).filter(Note.alias == alias).first()  # type: ignore

    def add_note(self, title: str, content: str, alias: str) -> None:
        # if not content:
        #     resp = self.GET('new')
        # elif not alias:
        #     resp = self.POST('new', content=content, content_type='text/markdown')
        # else:
        # resp = self.POST(f'new/{alias}', content=content, content_type='text/markdown')
        # resp.raise_for_status()
        note = {
            'short_id': alias,
            'alias': alias,
        }
        self.get_or_create(Note, **note, defaults={
            'id': uuid.uuid4(),
            '_title': title,
            'content': content,
            'created_at': datetime.now(),
            'owner_id': hedgedoc.get_current_user().id,
        })

    def get_ref_id(self, note: Note) -> str:
        """Return the URL-referenced ID given a Note.short_id or Note.alias."""
        if note.alias is not None:
            return note.alias  # type: ignore
        return parse(f'{self.server}{{}}', self.GET(note.short_id).headers['location'])[0]  # type: ignore

    # operations for Hedgedoc history
    def get_history(self) -> list[dict[str, t.Any]]:
        return self.GET('history').json()['history']

    # operations for Hedgedoc users
    def get_users(self) -> list[User]:
        return self.session.query(User).all()

    def get_current_user(self) -> User:
        if configs['HEDGEDOC_USER_EMAIL'] is None:
            exit_with_error('HEDGEDOC_USER_EMAIL is not set')
        return self.session.query(User).filter(User.email == configs['HEDGEDOC_USER_EMAIL']).first()  # type: ignore

    def refresh_alias(self, notes: list[Note] | None = None, dry_run: bool = False):
        """Re-alias notes based on their tags and title."""
        notes = notes or self.get_notes()
        print('Re-aliasing notes...')
        for note in notes:
            alias = Note.get_alias(title=note.title, tags=note.tags)
            if alias == note.alias:
                continue

            print(f'\t{note.title} ({note.alias} -> {alias})')
            if not dry_run:
                note.alias = alias  # type: ignore
                note.short_id = alias  # type: ignore
                self.session.commit()

        if not dry_run:
            self.refresh_history()

    def refresh_history(self, new_notes: list[Note] | None = None) -> None:
        """Refresh the browsing history based on the database."""
        history = [] if new_notes else self.get_history()
        history += [
            {
                'id': self.get_ref_id(note),
                'text': note.title,
                'time': int(datetime.now().timestamp()),
                'tags': note.tags,
            }
            for note in (new_notes or self.get_notes())
        ]
        resp = self.POST(
            'history',
            content=urlencode({'history': json.dumps(history)}),
            content_type='application/x-www-form-urlencoded',
        )
        resp.raise_for_status()


hedgedoc = Hedgedoc()

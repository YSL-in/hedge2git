import json
from datetime import datetime

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


class Hedgedoc:
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

    def get_history(self) -> list[dict]:
        return self.GET('history').json()['history']

    def add_history(self, note: Note) -> None:
        history = self.get_history()
        history.append({
            'id': self.get_ref_id(note),
            'text': note.title,
            'time': int(datetime.now().timestamp()),
            'tags': note.tags,
        })
        resp = self.POST('history', {'history': history})

    def GET(self, api: str) -> httpx.Response:
        return self.client.get(self.server.join(api))

    def POST(self, api: str, data: dict = {}) -> httpx.Response:
        return self.client.post(
            self.server.join(api),
            content=json.dumps(data),
            headers={'Content-Type': 'application/json'},
        )


hedgedoc_store = HedgedocStore()
hedgedoc = Hedgedoc()

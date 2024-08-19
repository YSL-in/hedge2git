import typing as t

import httpx
from parse import parse
from sqlalchemy import Column, create_engine
from sqlalchemy.orm import sessionmaker

from configs import configs

from .models import Note, User


class Hedgedoc:
    def __init__(self) -> None:
        db_type = configs['DB_TYPE']
        db_user = configs['DB_USER']
        db_pass = configs['DB_PASS']
        db_host = configs['DB_HOST']
        db_port = configs['DB_PORT']
        db_name = configs['DB_NAME']
        engine = create_engine(f'{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}', future=True)
        self.session = sessionmaker(bind=engine)()
        self.server = httpx.URL(configs['HEDGEDOC_SERVER'])

    def get_notes(self) -> t.List[Note]:
        return self.session.query(Note).all()

    def get_users(self) -> t.List[User]:
        return self.session.query(User).all()

    def get_ref_id(self, note_id: Column[str]) -> str:
        """Return the URL-referenced ID given a Note.short_id or Note.alias."""
        resp = self.send_request(note_id)
        return parse(f'{self.server}{{}}', resp.headers['location'])[0]  # type: ignore

    def send_request(self, api, action: t.Literal['GET', 'POST'] = 'GET') -> httpx.Response:
        with httpx.Client() as client:
            print(f'send request: {self.server.join(api)}')
            client.post(self.server.join('login'), json={
                'email': configs['USER_EMAIL'],
                'password': configs['USER_PASSWORD'],
            })
            request = client.get if action == 'GET' else client.post
            return request(self.server.join(api))


hedgedoc = Hedgedoc()

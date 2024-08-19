import typing as t

from sqlalchemy import create_engine
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

    def get_notes(self) -> t.List[Note]:
        return self.session.query(Note).all()

    def get_users(self) -> t.List[User]:
        return self.session.query(User).all()


hedgedoc = Hedgedoc()

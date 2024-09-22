import csv
import re
import typing as t
from enum import StrEnum
from itertools import chain

import yaml
from sqlalchemy import (UUID, Column, Enum, ForeignKey, Integer, String, Text,
                        Time)
from sqlalchemy.orm import DeclarativeBase, declarative_base, relationship

Base: type[DeclarativeBase] = declarative_base()
T_Base = t.TypeVar('T_Base', bound=DeclarativeBase)


class NotePermissionEnum(StrEnum):
    freely = 'freely'
    editable = 'editable'
    limited = 'limited'
    locked = 'locked'
    protected = 'protected'
    private = 'private'


class Note(Base):
    __tablename__ = 'Notes'

    id = Column('id', UUID, primary_key=True)
    short_id = Column('shortid', String(length=255), nullable=False)
    alias = Column('alias', String(length=255))
    _title = Column('title', Text)
    content = Column('content', Text)
    created_at = Column('createdAt', Time)
    updated_at = Column('updatedAt', Time)
    deleted_at = Column('deletedAt', Time)
    # save_at = Column('saveAt', Time)

    view_count = Column('viewcount', Integer)

    owner_id = Column('ownerId', UUID)
    permission = Column('permission', Enum(NotePermissionEnum, name='enum_Notes_permission'), default='editable')
    last_change_user_id = Column('lastchangeuserId', ForeignKey('Users.id'))
    last_change_at = Column('lastchangeAt', Time)
    # authorship = Column('authorship', Text)

    owner = relationship('User', back_populates='notes', cascade='all')
    authors = relationship('Author', back_populates='note', cascade='all, delete-orphan')

    @property
    def title(self) -> str:
        # TODO: parse title and assign it back
        return '' if self._title == 'Untitled' else self._title  # type: ignore

    @property
    def tags(self) -> list[str]:
        return Note.get_tags(self.content)  # type: ignore

    @staticmethod
    def get_alias(*, title: str = '', tags: list[str] = [], content: str = '') -> str:
        """Generate a unique alias for a note."""
        def sanitized(part: str) -> str:
            # include the chinese charsets
            sanitized = re.sub(r'[^a-zA-Z0-9\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+', '-', part.strip()).lower()
            return sanitized.replace('--', '-')

        tags = tags or Note.get_tags(content)
        title = title or Note.get_title(content)
        return '--'.join(sanitized(t) for t in [*tags, title])

    @staticmethod
    def get_title(content: str) -> str:
        """Extract title from a markdown content."""
        if title := Note.get_meta(content).get('title'):
            return title.strip()  # type: ignore

        prev = ''
        template = r'^ *=+$'
        for line in content.split('\n'):
            if re.findall(template, line) and prev:
                return prev.strip()  # type: ignore
            prev = line
        return 'Untitled'

    @staticmethod
    def get_tags(content: str) -> list[str]:
        """Extract tags from a Markdown content."""
        if tags := Note.get_meta(content).get('tags'):
            return (
                [tag.strip() for tag in tags]
                if isinstance(tags, list)
                else [tag.strip() for tag in chain(*csv.reader([tags]))]
            )

        tags = []
        template = r'`([^`]*)`'
        for line in content.split('\n'):
            if raw_tags := line.partition('###### tags')[-1]:
                tags += [tag for tag in re.findall(template, raw_tags) if tag]
        return [tag.strip() for tag in dict.fromkeys(tags)]

    @staticmethod
    def get_meta(content: str) -> dict[str, str | list[str]]:
        """Extract YAML metadata from a Markdown content."""
        if not content.startswith('---'):
            return {}

        raw_meta = ''
        for line in content.split('\n')[1:]:
            if not line:
                continue
            if line.startswith('---'):
                break
            raw_meta += line + '\n'

        try:
            meta = yaml.safe_load(raw_meta)
        except yaml.YAMLError:
            return {}
        return meta if isinstance(meta, dict) else {}


class User(Base):
    __tablename__ = 'Users'

    id = Column('id', UUID, primary_key=True)
    profile_id = Column('profileid', String(length=255))
    profile = Column('profile', Text)
    email = Column('email', Text)
    password = Column('password', Text)
    history = Column('history', Text)
    created_at = Column('createdAt', Time)
    updated_at = Column('updatedAt', Time)

    access_token = Column('accessToken', Text)
    refresh_token = Column('refreshToken', Text)
    delete_token = Column('deleteToken', UUID)

    notes = relationship('Note', back_populates='owner', cascade='all, delete-orphan')
    authors = relationship('Author', back_populates='user', cascade='all, delete-orphan')


class Author(Base):
    __tablename__ = 'Authors'

    id = Column('id', Integer, primary_key=True)
    color = Column('color', String(length=255))
    note_id = Column('noteId', UUID, ForeignKey('Notes.id'))
    user_id = Column('userId', UUID, ForeignKey('Users.id'))
    created_at = Column('createdAt', Time)
    updated_at = Column('updatedAt', Time)

    note = relationship('Note', back_populates='authors', cascade='all')
    user = relationship('User', back_populates='authors', cascade='all')

# class Revision(Base): ...
# class SequelizedMeta(Base): ...
# class Session(Base): ...
# class Temp(Base): ...

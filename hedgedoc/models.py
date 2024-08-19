from sqlalchemy import UUID, Column, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import DeclarativeBase, declarative_base, relationship

Base: type[DeclarativeBase] = declarative_base()


class Note(Base):
    __tablename__ = 'Notes'

    id = Column('id', UUID, primary_key=True)
    short_id = Column('shortid', String(length=255), nullable=False)
    title = Column('title', Text)
    content = Column('content', Text)
    created_at = Column('createdAt', Time)
    updated_at = Column('updatedAt', Time)
    deleted_at = Column('deletedAt', Time)
    # save_at = Column('saveAt', Time)

    view_count = Column('viewcount', Integer)

    owner_id = Column('ownerId', UUID)
    # permission = Column('permission', EnumNotePermission)
    last_change_user_id = Column('lastchangeuserId', ForeignKey('Users.id'))
    last_change_at = Column('lastchangeAt', Time)
    # authorship = Column('authorship', Text)

    owner = relationship('User', back_populates='notes', cascade='all')
    authors = relationship('Author', back_populates='note', cascade='all, delete-orphan')


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

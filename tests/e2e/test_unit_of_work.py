import dataclasses

import pytest
import sqlalchemy as sa
from sqlalchemy import orm

from lime_uow import *

metadata = sa.MetaData()

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("name", sa.String, primary_key=True),
)


@dataclasses.dataclass(unsafe_hash=True)
class User:
    name: str


@pytest.fixture
def engine():
    engine = sa.engine.create_engine("sqlite://", echo=True)
    metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(engine):
    orm.mapper(User, user_table)
    yield orm.sessionmaker(bind=engine)
    orm.clear_mappers()


def test_unit_of_work_save(session_factory: orm.sessionmaker):
    resource = SqlAlchemySessionResource(
        name="user_session", session_factory=session_factory
    )
    with UnitOfWork(resource) as uow:
        session = uow.get_resource("user_session")
        session.add(User("Mark"))
        uow.save()

    session = session_factory()
    actual = session.query(User).all()
    assert actual == [User(name="Mark")]


def test_unit_of_work_rollback(session_factory: orm.sessionmaker):
    resource = SqlAlchemySessionResource(
        name="user_session", session_factory=session_factory
    )
    with UnitOfWork(resource) as uow:
        session = uow.get_resource("user_session")
        session.add(User("Mark"))
        uow.rollback()

    session = session_factory()
    actual = session.query(User).all()
    assert actual == []

import dataclasses

import pytest
from sqlalchemy import orm
import sqlalchemy as sa

metadata = sa.MetaData()

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
)


@dataclasses.dataclass(unsafe_hash=True)
class User:
    id: int
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


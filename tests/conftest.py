import dataclasses

import pytest
import sqlalchemy as sa
import typing
from sqlalchemy import orm
from sqlalchemy.orm.base import _is_mapped_class

from lime_uow import resources

metadata = sa.MetaData()

user_table = sa.Table(
    "users",
    metadata,
    sa.Column("user_id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String, nullable=False),
)


@dataclasses.dataclass(unsafe_hash=True)
class User:
    user_id: int
    name: str


@pytest.fixture
def initial_users() -> typing.List[User]:
    return [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
    ]


class UserRepository(resources.SqlAlchemyRepository[User]):
    @classmethod
    def resource_name(cls) -> str:
        return "user_repository"

    def __init__(self, session: orm.Session):
        self.session = session

        super().__init__(entity=User, session=session)


@pytest.fixture
def engine() -> sa.engine.Engine:
    engine = sa.engine.create_engine("sqlite://", echo=True)
    metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(engine) -> orm.sessionmaker:
    orm.mapper(User, user_table)
    yield orm.sessionmaker(bind=engine)
    orm.clear_mappers()


@pytest.fixture
def user_repo(session_factory: orm.sessionmaker, initial_users: typing.List[User]) -> UserRepository:
    if not _is_mapped_class(User):
        orm.mapper(User, user_table)
    session: orm.Session = session_factory()
    session.add_all(initial_users)
    session.commit()
    return UserRepository(session)

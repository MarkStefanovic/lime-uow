import abc
import dataclasses

import pytest
import sqlalchemy as sa
import typing
from sqlalchemy import orm

from lime_uow import resources, unit_of_work

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


class AbstractUserRepository(resources.SqlAlchemyRepository[User], abc.ABC):
    @abc.abstractmethod
    def get_first(self) -> User:
        raise NotImplementedError


class UserRepository(AbstractUserRepository):
    def __init__(self, session: orm.Session):
        super().__init__(session)

    def get_first(self) -> User:
        return next(self.all())


class TestUnitOfWork(unit_of_work.SqlAlchemyUnitOfWork):
    def create_resources(self) -> typing.AbstractSet[resources.Resource[typing.Any]]:
        return {UserRepository(self.session)}


@pytest.fixture
def engine() -> sa.engine.Engine:
    engine = sa.engine.create_engine("sqlite://", echo=True)
    metadata.create_all(bind=engine)
    return engine


@pytest.fixture
def session_factory(engine) -> orm.sessionmaker:
    orm.mapper(User, user_table)
    factory = orm.sessionmaker(bind=engine)
    session = factory()
    session.add_all(
        [
            User(user_id=1, name="Mark"),
            User(user_id=2, name="Mandie"),
        ]
    )
    session.commit()
    yield orm.sessionmaker(bind=engine)
    orm.clear_mappers()


@pytest.fixture
def user_repo(session_factory: orm.sessionmaker) -> UserRepository:
    return UserRepository(session_factory())


@pytest.fixture
def user_uow(session_factory: orm.sessionmaker) -> TestUnitOfWork:
    return TestUnitOfWork(session_factory)

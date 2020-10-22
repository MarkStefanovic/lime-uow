from __future__ import annotations

import typing

import lime_uow as lu
from tests.conftest import User, UserRepository

from sqlalchemy import orm


class SqlAlchemyUserSession(lu.SqlAlchemySession):
    def __init__(self, session_factory: orm.sessionmaker, /):
        self._session_factory = session_factory
        super().__init__(session_factory)

    @classmethod
    def interface(cls) -> typing.Type[SqlAlchemyUserSession]:
        return cls


class TestUnitOfWork(lu.UnitOfWork):
    def __init__(
        self,
        session_factory: orm.sessionmaker,
    ):
        super().__init__(
            lu.SharedResources(
                SqlAlchemyUserSession(session_factory)
            )
        )

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.AbstractSet[lu.Resource[typing.Any]]:
        return {UserRepository(shared_resources.get(SqlAlchemyUserSession))}


def test_unit_of_work_save(session_factory: orm.sessionmaker):
    with TestUnitOfWork(session_factory) as uow:
        repo = uow.get_resource(UserRepository)
        repo.add(User(user_id=999, name="Steve"))
        uow.save()

    actual = session_factory().query(User).all()
    expected = [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        User(user_id=999, name="Steve"),
    ]
    assert actual == expected


def test_unit_of_work_rollback(session_factory: orm.sessionmaker):
    with TestUnitOfWork(session_factory) as uow:
        repo = uow.get_resource(UserRepository)
        repo.add(User(999, "Mark"))
        uow.rollback()

    actual = session_factory().query(User).all()
    expected = [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    assert actual == expected

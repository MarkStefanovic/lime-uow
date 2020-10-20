import typing

from lime_uow import resources, shared_resource_manager, unit_of_work
from tests.conftest import User, UserRepository

from sqlalchemy import orm


class SqlAlchemyUserSession(resources.SqlAlchemySession):
    def __init__(self, session_factory: orm.sessionmaker, /):
        self._session_factory = session_factory
        super().__init__(session_factory)


class TestUnitOfWork(unit_of_work.UnitOfWork):
    def __init__(
        self,
        session_factory: orm.sessionmaker,
    ):
        super().__init__(
            shared_resource_manager.SharedResources(
                SqlAlchemyUserSession(session_factory)
            )
        )

    def create_resources(
        self, shared_resources: shared_resource_manager.SharedResources
    ) -> typing.AbstractSet[resources.Resource[typing.Any]]:
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

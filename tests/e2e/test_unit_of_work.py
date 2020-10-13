import typing

from lime_uow import *
from tests.conftest import User, UserRepository

from sqlalchemy import orm


class TestUnitOfWork(SqlAlchemyUnitOfWork):
    def __init__(
        self,
        session_factory: orm.sessionmaker,
    ):
        super().__init__(session_factory)

    def create_resources(self) -> typing.Set[resources.Resource[typing.Any]]:
        return {
            UserRepository(session=self.session)
        }


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

from sqlalchemy import orm

from lime_uow import *
from tests.conftest import User


def test_unit_of_work_save(session_factory: orm.sessionmaker):
    session = session_factory()
    resource = SqlAlchemyRepository(
        entity=User,
        name="user_session",
        session=session,
    )
    with UnitOfWork(resource) as uow:
        session = uow.get_resource("user_session")
        session.add(User(id=1, name="Mark"))
        uow.save()

    session = session_factory()
    actual = session.query(User).all()
    assert actual == [User(id=1, name="Mark")]


def test_unit_of_work_rollback(session_factory: orm.sessionmaker):
    session = session_factory()
    resource = SqlAlchemyRepository(
        entity=User,
        name="user_session",
        session=session,
    )
    with UnitOfWork(resource) as uow:
        session = uow.get_resource("user_session")
        session.add(User(1, "Mark"))
        uow.rollback()

    session = session_factory()
    actual = session.query(User).all()
    assert actual == []

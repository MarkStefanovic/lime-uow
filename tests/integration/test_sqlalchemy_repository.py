import pytest
from sqlalchemy import orm

from lime_uow import UnitOfWork, exception
from lime_uow.resrc import SqlAlchemyRepository
from tests.conftest import User


def test_sqlalchemy_repository_raises_uninitialized_exception_outise_transaction(
    session_factory: orm.sessionmaker,
):
    session = session_factory()
    repo = SqlAlchemyRepository(
        name="user_repo",
        entity=User,
        session=session,
    )
    with pytest.raises(
        exception.MissingTransactionBlock,
        match="Attempted to edit repository outside of a transaction.",
    ):
        repo.add(User(id=1, name="Mark"))


def test_sqlalchemy_repository_add_works(
    session_factory: orm.sessionmaker,
):
    session = session_factory()
    with UnitOfWork(
        SqlAlchemyRepository(name="user_repo", entity=User, session=session)
    ) as uow:
        repo = uow.get_resource("user_repo")
        repo.add(User(id=1, name="Mark"))
        repo.add(User(id=2, name="Mandie"))
        uow.save()

    actual = session.query(User).all()
    assert actual == [User(id=1, name="Mark"), User(id=2, name="Mandie")]


def test_sqlalchemy_repository_get_works(
    session_factory: orm.sessionmaker,
):
    session = session_factory()
    session.add(User(id=1, name="Mandie"))
    session.add(User(id=2, name="Mark"))
    session.commit()

    with UnitOfWork(
        SqlAlchemyRepository(name="user_repo", entity=User, session=session)
    ) as uow:
        repo: SqlAlchemyRepository[User] = uow.get_resource("user_repo")
        actual = repo.get(2)
    print(f"{actual=}")
    assert actual == User(id=2, name="Mark")

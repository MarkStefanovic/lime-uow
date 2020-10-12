from lime_uow import *
from tests.conftest import User, UserRepository


def test_unit_of_work_save(user_repo: UserRepository):
    with UnitOfWork(user_repo) as uow:
        with uow.get_resource(UserRepository) as repo:
            repo.add(User(user_id=999, name="Steve"))
            uow.save()

    actual = user_repo.session.query(User).all()
    assert actual == [
        User(user_id=1, name="Mark"),
        User(user_id=2, name="Mandie"),
        User(user_id=999, name="Steve"),
    ]


def test_unit_of_work_rollback(user_repo: UserRepository):
    with UnitOfWork(user_repo) as uow:
        with uow.get_resource(UserRepository) as repo:
            repo.add(User(999, "Mark"))
            uow.rollback()

    actual = user_repo.session.query(User).all()
    expected = [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie")]
    assert actual == expected

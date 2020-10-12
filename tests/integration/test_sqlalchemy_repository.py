from lime_uow import exceptions, unit_of_work
from tests.conftest import *


def test_sqlalchemy_repository_raises_uninitialized_exception_outside_transaction(
    user_repo: UserRepository,
):
    with pytest.raises(
        exceptions.MissingTransactionBlock,
        match="Attempted to edit repository outside of a transaction.",
    ):
        user_repo.add(User(user_id=1, name="Mark"))


def test_sqlalchemy_repository_add_works_inside_context_manager(
    user_repo: UserRepository,
):
    new_user = User(user_id=999, name="Steve")
    with unit_of_work.UnitOfWork(user_repo) as uow:
        repo = uow.get_resource(UserRepository)
        repo.add(new_user)
        uow.save()

    actual = user_repo.session.query(User).all()
    assert actual == [User(user_id=1, name="Mark"), User(user_id=2, name="Mandie"), new_user]


def test_sqlalchemy_repository_get_resource_by_name_works(
    user_repo: UserRepository,
):
    with unit_of_work.UnitOfWork(user_repo) as uow:
        repo: resources.SqlAlchemyRepository[User] = uow.get_resource_by_name(
            "user_repo"
        )
        actual = repo.get(2)
    expected = User(user_id=2, name='Mandie')
    assert actual == expected

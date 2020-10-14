from tests.conftest import *


def test_sqlalchemy_repository_get_resource_by_type_works(
    user_uow: TestUnitOfWork,
):
    with user_uow as uow:
        repo = uow.get_resource(AbstractUserRepository)  # type: ignore # see https://github.com/python/mypy/issues/5374

    assert type(repo) is UserRepository


def test_sqlalchemy_repository_get_resource_by_name_works(
    user_uow: TestUnitOfWork,
):
    with user_uow as uow:
        repo = uow.get_resource_by_name("AbstractUserRepository")

    assert type(repo) is UserRepository

import abc

import typing

from lime_uow import resources, unit_of_work


class AbstractDummy(resources.Resource[typing.Any], abc.ABC):
    @abc.abstractmethod
    def do_something(self):
        raise NotImplementedError


class DummyImpl(AbstractDummy):
    def rollback(self) -> None:
        pass

    def save(self) -> None:
        pass

    def do_something(self):
        print("LOUD NOISES!")


class DumyUOW(unit_of_work.UnitOfWork):
    def create_resources(self) -> typing.AbstractSet[resources.Resource[typing.Any]]:
        return {DummyImpl()}


def test_sqlalchemy_repository_get_resource_by_type_works():
    with DumyUOW() as uow:
        repo = uow.get_resource(AbstractDummy)  # type: ignore  # see mypy issue 5374

    assert type(repo) is DummyImpl


def test_sqlalchemy_repository_get_resource_by_name_works():
    with DumyUOW() as uow:
        repo = uow.get_resource_by_name("AbstractDummy")

    assert type(repo) is DummyImpl

from __future__ import annotations

import abc
import typing

from lime_uow import resources, unit_of_work
from lime_uow.unit_of_work import shared_resource_manager


class AbstractDummyResource(resources.Resource[typing.Any], abc.ABC):
    @abc.abstractmethod
    def do_something(self):
        raise NotImplementedError


class DummyResource(AbstractDummyResource):
    def __init__(self, shared_resource: str):
        self._shared_resource = shared_resource

    def rollback(self) -> None:
        pass

    def save(self) -> None:
        pass

    def do_something(self):
        print(self._shared_resource)


class AbstractDummySharedResource(resources.SharedResource[str], abc.ABC):
    @abc.abstractmethod
    def do_something(self):
        raise NotImplementedError


class DummySharedResource(AbstractDummySharedResource):
    def __init__(self):
        self.is_open = False

    def do_something(self):
        pass

    def open(self) -> str:
        self.is_open = True
        return "test_resource"

    def close(self) -> None:
        self.is_open = False

    def rollback(self) -> None:
        pass

    def save(self) -> None:
        pass


class DummyUOW(unit_of_work.UnitOfWork):
    def __init__(self):
        super().__init__(shared_resource_manager.SharedResources(DummySharedResource()))

    def create_resources(
        self, shared_resources: shared_resource_manager.SharedResources
    ) -> typing.Set[resources.Resource[typing.Any]]:
        shared_resource = shared_resources.get(DummySharedResource)
        return {DummyResource(shared_resource)}


def test_unit_of_work_get_resource():
    with DummyUOW() as uow:
        repo = uow.get_resource(AbstractDummyResource)  # type: ignore  # see mypy issue 5374
    assert type(repo) is DummyResource


def test_unit_of_work_repository_get_resource_by_name():
    with DummyUOW() as uow:
        repo = uow.get_resource_by_name(AbstractDummyResource.__name__)
    assert type(repo) is DummyResource

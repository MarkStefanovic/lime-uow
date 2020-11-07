from __future__ import annotations

import abc
import typing

import lime_uow as lu
from lime_uow.resources.resource import T


class AbstractDummyResource(lu.Resource[typing.Any], abc.ABC):
    @abc.abstractmethod
    def do_something(self):
        raise NotImplementedError


class DummyResource(AbstractDummyResource):
    def __init__(self, shared_resource: str):
        self._shared_resource = shared_resource

    def close(self) -> None:
        pass

    def open(self) -> T:
        pass

    @classmethod
    def interface(cls) -> typing.Type[AbstractDummyResource]:
        return AbstractDummyResource

    def rollback(self) -> None:
        pass

    def save(self) -> None:
        pass

    def do_something(self):
        print(self._shared_resource)


class AbstractDummySharedResource(lu.Resource[str], abc.ABC):
    @abc.abstractmethod
    def do_something(self):
        raise NotImplementedError


class DummySharedResource(AbstractDummySharedResource):
    def __init__(self):
        self.is_open = False

    def do_something(self):
        pass

    @classmethod
    def interface(cls) -> typing.Type[AbstractDummySharedResource]:
        return AbstractDummySharedResource

    def open(self) -> str:
        self.is_open = True
        return "test_resource"

    def close(self) -> None:
        self.is_open = False

    def rollback(self) -> None:
        pass

    def save(self) -> None:
        pass


class DummyUOW(lu.UnitOfWork):
    def __init__(self):
        super().__init__(lu.SharedResources(DummySharedResource()))

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.Set[lu.Resource[typing.Any]]:
        shared_resource = shared_resources.get(DummySharedResource)
        return {DummyResource(shared_resource)}


def test_unit_of_work_get_resource_given_interface():
    with DummyUOW() as uow:
        repo = uow.get_resource(AbstractDummyResource)  # type: ignore  # see mypy issue 5374
    assert type(repo) is DummyResource


def test_unit_of_work_get_resource_given_implementation():
    with DummyUOW() as uow:
        repo = uow.get_resource(DummyResource)
    assert type(repo) is DummyResource

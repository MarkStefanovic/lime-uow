from __future__ import annotations

import typing

import pytest

import lime_uow as lu
from lime_uow.resources.resource import T


class Recorder:
    def __init__(self):
        self.events = []

    def do_something(self, action: str):
        self.events.append(action)


class TestResource(lu.Resource[Recorder]):
    def __init__(self, shared_resource: str):
        self._shared_resource = shared_resource
        self.handle = Recorder()
        super().__init__()

    @classmethod
    def interface(cls) -> typing.Type[TestResource]:
        return cls

    def close(self) -> None:
        pass

    def open(self) -> T:
        pass

    def rollback(self) -> None:
        self.handle.events.append("rollback")

    def save(self) -> None:
        self.handle.events.append("save")


class TestSharedResource(lu.Resource[str]):
    def __init__(self, value: str):
        self.value = value
        self._prior_value = value

    @classmethod
    def interface(cls) -> typing.Type[TestSharedResource]:
        return cls

    def open(self) -> str:
        return self.value

    def close(self) -> None:
        pass

    def rollback(self) -> None:
        self.value = self._prior_value

    def save(self) -> None:
        self._prior_value = self.value


class TestUOW(lu.UnitOfWork):
    def __init__(self):
        super().__init__(
            lu.SharedResources(TestSharedResource("test"))
        )

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.Iterable[lu.Resource[typing.Any]]:
        return [TestResource(shared_resources.get(TestSharedResource))]


class DuplicateJobTestUOW(lu.UnitOfWork):
    def __init__(self):
        super().__init__(
            lu.SharedResources(TestSharedResource("test"))
        )

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.Iterable[lu.Resource[typing.Any]]:
        return [
            TestResource(shared_resources.get(TestSharedResource)),
            TestResource(shared_resources.get(TestSharedResource)),
        ]


def test_uow_raises_error_when_duplicate_resources_given():
    with pytest.raises(
        lu.exceptions.MultipleRegisteredImplementations,
        match="Resource names must be unique, but found the following duplicates: TestResource = 2",
    ):
        with DuplicateJobTestUOW() as uow:
            uow.save()


def test_unit_of_work_save():
    uow = TestUOW()
    with uow:
        r = uow.get(TestResource)
        uow.save()

    assert r.handle.events == ["save", "rollback"]


def test_unit_of_work_rollback():
    with TestUOW() as uow:
        r = uow.get(TestResource)
        uow.rollback()

    assert r.handle.events == [
        "rollback",
        "rollback",
    ]

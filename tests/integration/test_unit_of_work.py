from __future__ import annotations

import typing

import pytest

import lime_uow as lu


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

    def open(self) -> Recorder:
        return self.handle

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
        super().__init__()

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.Iterable[lu.Resource[typing.Any]]:
        return [TestResource(shared_resources.get(TestSharedResource))]

    def create_shared_resources(self) -> typing.List[lu.Resource[typing.Any]]:
        return [TestSharedResource("test")]


class DuplicateJobTestUOW(lu.UnitOfWork):
    def __init__(self):
        super().__init__()

    def create_resources(
        self, shared_resources: lu.SharedResources
    ) -> typing.Iterable[lu.Resource[typing.Any]]:
        return [
            TestResource(shared_resources.get(TestSharedResource)),
            TestResource(shared_resources.get(TestSharedResource)),
        ]

    def create_shared_resources(self) -> typing.List[lu.Resource[typing.Any]]:
        return [TestSharedResource("test")]


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
        r = uow.get(TestResource)  # type: ignore
        uow.save()

    assert r.events == ["save", "rollback"]


def test_unit_of_work_rollback():
    with TestUOW() as uow:
        r = uow.get(TestResource)  # type: ignore
        uow.rollback()

    assert r.events == [
        "rollback",
        "rollback",
    ]

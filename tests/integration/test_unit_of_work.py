import typing

import pytest

from lime_uow import exceptions, resources, unit_of_work


class Recorder:
    def __init__(self):
        self.events = []

    def do_something(self, action: str):
        self.events.append(action)


class TestResource(resources.Resource[Recorder]):
    def __init__(self):
        self.handle = Recorder()
        super().__init__()

    @classmethod
    def resource_name(cls) -> str:
        return cls.__name__

    def rollback(self) -> None:
        self.handle.events.append("rollback")

    def save(self) -> None:
        self.handle.events.append("save")


class TestUOW(unit_of_work.UnitOfWork):
    def __init__(self, /, *resource: resources.Resource[typing.Any]):
        super().__init__()
        self._resources = list(resource)

    def create_resources(self) -> typing.List[resources.Resource[typing.Any]]:  # type: ignore
        return self._resources


def test_uow_raises_error_when_duplicate_resources_given():
    with pytest.raises(
        exceptions.DuplicateResourceNames,
        match="Resource names must be unique, but found the following duplicates: TestResource = 2",
    ):
        with TestUOW(TestResource(), TestResource()) as uow:
            uow.save()


def test_unit_of_work_save():
    uow = TestUOW(TestResource())
    with uow:
        r = uow.get_resource(TestResource)
        uow.save()

    assert r.handle.events == ["save", "rollback"]


def test_unit_of_work_rollback():
    with TestUOW(TestResource()) as uow:
        r = uow.get_resource(TestResource)
        uow.rollback()

    assert r.handle.events == [
        "rollback",
        "rollback",
    ]

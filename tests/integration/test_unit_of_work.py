import pytest

from lime_uow import *


class Recorder:
    def __init__(self):
        self.events = []

    def do_something(self, action: str):
        self.events.append(action)


class TestResource(Resource[Recorder]):
    def __init__(self, name: str):
        self._name = name
        self._handle = Recorder()
        super().__init__()

    def close(self) -> None:
        self._handle.events.append("close")

    @property
    def name(self) -> str:
        return self._name

    def open(self) -> Recorder:
        self._handle.events.append("open")
        return self._handle

    @classmethod
    def resource_name(cls) -> str:
        return cls.__name__

    def rollback(self) -> None:
        self._handle.events.append("rollback")

    def save(self) -> None:
        self._handle.events.append("save")


def test_uow_raises_error_when_duplicate_resource_names_are_given():
    with pytest.raises(
        exceptions.DuplicateResourceNames,
        match="Resource names must be unique, but found the following duplicates: TestResource = 2",
    ):
        UnitOfWork(
            TestResource("a"),
            TestResource("c"),
        )


def test_unit_of_work_save():
    uow = UnitOfWork(TestResource("a"))
    with uow.get_resource(TestResource) as resource:
        resource.events.append("do_something_a")
        uow.save()

    assert resource.events == ["open", "do_something_a", "save", "rollback", "close"]


def test_unit_of_work_rollback():
    uow = UnitOfWork(TestResource("a"))
    with uow.get_resource(TestResource) as resource:
        resource.do_something("do_something_a")
        uow.rollback()

    assert resource.events == [
        "open",
        "do_something_a",
        "rollback",
        "rollback",
        "close",
    ]

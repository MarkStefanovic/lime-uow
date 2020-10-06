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

    def close(self) -> None:
        self._handle.events.append("close")

    @property
    def name(self) -> str:
        return self._name

    def open(self) -> Recorder:
        self._handle.events.append("open")
        return self._handle

    def rollback(self) -> None:
        self._handle.events.append("rollback")

    def save(self) -> None:
        self._handle.events.append("save")


def test_unit_of_work_raises_error_when_used_outside_with_block():
    uow = UnitOfWork(
        TestResource("a"),
        TestResource("b"),
        TestResource("c"),
    )
    with pytest.raises(
        exception.MissingTransactionBlock,
        match="Attempted to rollback a UnitOfWork instance outside a `with` block.",
    ):
        uow.rollback()


def test_unit_of_work_save():
    with UnitOfWork(
        TestResource("a"),
        TestResource("b"),
        TestResource("c"),
    ) as uow:
        a = uow.get_resource("a")
        a.events.append("do_something_a")
        b = uow.get_resource("b")
        b.events.append("do_something_b")
        uow.save()

    assert a.events == ["open", "do_something_a", "save", "rollback", "close"]
    assert b.events == ["open", "do_something_b", "save", "rollback", "close"]


def test_unit_of_work_rollback():
    with UnitOfWork(
        TestResource("a"),
        TestResource("b"),
        TestResource("c"),
    ) as uow:
        a = uow.get_resource("a")
        a.do_something("do_something_a")
        b = uow.get_resource("b")
        b.do_something("do_something_b")
        uow.rollback()

    assert a.events == ["open", "do_something_a", "rollback", "rollback", "close"]
    assert b.events == ["open", "do_something_b", "rollback", "rollback", "close"]

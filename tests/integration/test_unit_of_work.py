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


def test_uow_raises_error_when_duplicate_resource_names_are_given():
    with pytest.raises(
        exceptions.DuplicateResourceNames,
        match="Resource names must be unique, but found the following duplicates: a = 2, c = 2",
    ):
        UnitOfWork(
            TestResource("a"),
            TestResource("c"),
            TestResource("c"),
            TestResource("a"),
            TestResource("b"),
        )


def test_unit_of_work_raises_error_when_used_outside_with_block():
    uow = UnitOfWork(
        TestResource("a"),
        TestResource("b"),
        TestResource("c"),
    )
    with pytest.raises(
        exceptions.MissingTransactionBlock,
        match="Attempted to rollback a UnitOfWork instance outside a `with` block.",
    ):
        uow.rollback()


def test_unit_of_work_save():
    with UnitOfWork(
        TestResource("a"),
        TestResource("b"),
        TestResource("c"),
    ) as uow:
        a = uow.get_resource_by_name("a")
        a.events.append("do_something_a")
        b = uow.get_resource_by_name("b")
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
        a = uow.get_resource_by_name("a")
        a.do_something("do_something_a")
        b = uow.get_resource_by_name("b")
        b.do_something("do_something_b")
        uow.rollback()

    assert a.events == ["open", "do_something_a", "rollback", "rollback", "close"]
    assert b.events == ["open", "do_something_b", "rollback", "rollback", "close"]


def test_unit_of_work_with_missing_resource_name_raises_error_on_from_uow():
    class DummyRepository(DictRepository):
        def __init__(self):
            super().__init__(
                initial_values={"a": 1, "b": 2, "c": 3},
                key_fn=lambda k: k,
            )

    expected_error_message = (
        "The class, DummyRepository, must override the __resource_name__ class attribute in order "
        "to use the .from_uow class method."
    )
    with pytest.raises(exceptions.ClassMissingResourceNameOverride, match=expected_error_message):
        with UnitOfWork(DummyRepository()) as uow:
            uow.get_resource(DummyRepository)

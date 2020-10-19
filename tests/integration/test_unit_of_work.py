import typing

import pytest

from lime_uow import exceptions, resources, unit_of_work


class Recorder:
    def __init__(self):
        self.events = []

    def do_something(self, action: str):
        self.events.append(action)


class TestResource(resources.Resource[Recorder]):
    def __init__(self, shared_resource: str):
        self._shared_resource = shared_resource
        self.handle = Recorder()
        super().__init__()

    @classmethod
    def resource_name(cls) -> str:
        return cls.__name__

    def rollback(self) -> None:
        self.handle.events.append("rollback")

    def save(self) -> None:
        self.handle.events.append("save")


class TestSharedResource(resources.SharedResource[str]):
    def __init__(self, value: str):
        self.value = value
        self._prior_value = value

    def open(self) -> str:
        return self.value

    def close(self) -> None:
        pass

    def rollback(self) -> None:
        self.value = self._prior_value

    def save(self) -> None:
        self._prior_value = self.value


class TestUOW(unit_of_work.UnitOfWork):
    def __init__(self):
        super().__init__()

    def create_resources(
        self, shared_resources: unit_of_work.SharedResources
    ) -> typing.Iterable[resources.Resource[typing.Any]]:
        return [TestResource(shared_resources.get(TestSharedResource))]

    def create_shared_resources(
        self,
    ) -> typing.Iterable[resources.SharedResource[typing.Any]]:
        return [TestSharedResource("test")]


class DuplicateJobTestUOW(unit_of_work.UnitOfWork):
    def __init__(self):
        super().__init__()

    def create_resources(
        self, shared_resources: unit_of_work.SharedResources
    ) -> typing.Iterable[resources.Resource[typing.Any]]:
        return [
            TestResource(shared_resources.get(TestSharedResource)),
            TestResource(shared_resources.get(TestSharedResource)),
        ]

    def create_shared_resources(
        self,
    ) -> typing.Iterable[resources.SharedResource[typing.Any]]:
        return [TestSharedResource("test")]


def test_uow_raises_error_when_duplicate_resources_given():
    with pytest.raises(
        exceptions.DuplicateResourceNames,
        match="Resource names must be unique, but found the following duplicates: TestResource = 2",
    ):
        with DuplicateJobTestUOW() as uow:
            uow.save()


def test_unit_of_work_save():
    uow = TestUOW()
    with uow:
        r = uow.get_resource(TestResource)
        uow.save()

    assert r.handle.events == ["save", "rollback"]


def test_unit_of_work_rollback():
    with TestUOW() as uow:
        r = uow.get_resource(TestResource)
        uow.rollback()

    assert r.handle.events == [
        "rollback",
        "rollback",
    ]

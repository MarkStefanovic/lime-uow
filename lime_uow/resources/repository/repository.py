import abc
import typing

from lime_uow.resources import resource

EntityType = typing.TypeVar("EntityType")


__all__ = ("Repository",)


class Repository(resource.Resource[None], abc.ABC, typing.Generic[EntityType]):
    """Interface to access elements of a collection"""

    @abc.abstractmethod
    def add(self, /, item: EntityType) -> EntityType:
        raise NotImplementedError

    @abc.abstractmethod
    def add_all(self, /, items: typing.Collection[EntityType]) -> typing.Collection[EntityType]:
        raise NotImplementedError

    @abc.abstractmethod
    def all(self) -> typing.Iterable[EntityType]:
        raise NotImplementedError

    def close(self) -> None:
        pass

    @abc.abstractmethod
    def delete(self, /, item: EntityType) -> EntityType:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        raise NotImplementedError

    def open(self) -> None:
        pass

    @abc.abstractmethod
    def set_all(self, /, items: typing.Collection[EntityType]) -> typing.Collection[EntityType]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, /, item: EntityType) -> EntityType:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, /, item_id: typing.Any) -> EntityType:
        raise NotImplementedError

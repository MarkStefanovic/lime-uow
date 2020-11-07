import abc
import typing

from lime_uow.resources import resource

E = typing.TypeVar("E")


__all__ = ("Repository",)


class Repository(resource.Resource[E], abc.ABC, typing.Generic[E]):
    """Interface to access elements of a collection"""

    @abc.abstractmethod
    def add(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def add_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        raise NotImplementedError

    @abc.abstractmethod
    def all(self) -> typing.Iterable[E]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def set_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, item_id: typing.Any, /) -> E:
        raise NotImplementedError

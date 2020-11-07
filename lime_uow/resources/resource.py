from __future__ import annotations

import abc
import typing

from lime_uow import exceptions

__all__ = (
    "Resource",
    "check_for_ambiguous_implementations",
)

T = typing.TypeVar("T", covariant=True)


class Resource(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def interface(cls) -> typing.Type[Resource[T]]:
        raise NotImplementedError

    @abc.abstractmethod
    def open(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def save(self) -> None:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            # noinspection PyTypeChecker
            return (
                self.__class__.interface()
                == typing.cast(Resource[typing.Any], other).__class__.interface()
            )
        else:
            return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        else:
            return not result

    def __hash__(self) -> int:
        return hash(self.__class__.interface())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.__class__.interface()}"


def check_for_ambiguous_implementations(
    rs: typing.Iterable[Resource[typing.Any]], /
) -> None:
    names = [r.__class__.interface().__name__ for r in rs]
    duplicate_names = {name: ct for name in names if (ct := names.count(name)) > 1}
    if duplicate_names:
        raise exceptions.MultipleRegisteredImplementations(duplicate_names)

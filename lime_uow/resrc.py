from __future__ import annotations
import abc
import typing

from sqlalchemy import orm

__all__ = (
    "Resource",
    "SqlAlchemyRepository",
)

from lime_uow import exception

T = typing.TypeVar("T", covariant=True)
E = typing.TypeVar("E")


class Resource(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def open(self) -> Resource[T]:
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
            return self.name == typing.cast(Resource, other).name
        else:
            return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return NotImplemented
        else:
            return not result

    def __hash__(self) -> int:
        return hash(self.name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


class SqlAlchemyRepository(Resource[typing.Any], typing.Generic[E]):
    def __init__(
        self,
        name: str,
        entity: typing.Type[E],
        session: orm.Session,
    ):
        super().__init__()

        self._entity = entity
        self._name = name
        self._session = session

        self.in_transaction = False

    def __enter__(self):
        return self.open()

    def __exit__(self, *args):
        return self.close()

    def close(self) -> None:
        self.in_transaction = False
        # self._session.close()

    @property
    def name(self) -> str:
        return self._name

    def open(self) -> SqlAlchemyRepository[E]:
        self.in_transaction = True
        return self

    def rollback(self) -> None:
        if not self.in_transaction:
            raise exception.MissingTransactionBlock(
                "Attempted to rollback a repository outside of a transaction."
            )
        else:
            self._session.rollback()

    def save(self) -> None:
        if not self.in_transaction:
            raise exception.MissingTransactionBlock(
                "Attempted to save a repository outside of a transaction."
            )
        else:
            self._session.commit()

    def add(self, item: E, /) -> E:
        if not self.in_transaction:
            raise exception.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )
        else:
            self._session.add(item)
            return item

    def delete(self, item: E, /) -> E:
        if not self.in_transaction:
            raise exception.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )
        else:
            self._session.delete(item)
            return item

    def update(self, item: E, /) -> E:
        if not self.in_transaction:
            raise exception.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )
        else:
            self._session.merge(item)
            return item

    def get(self, item_id: typing.Any, /) -> E:
        return self._session.query(self._entity).get(item_id)

    def where(self, predicate: typing.Any, /) -> typing.List[E]:
        return self._session.query(self._entity).filter(predicate).all()

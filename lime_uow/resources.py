from __future__ import annotations

import abc
import typing

from sqlalchemy import orm

__all__ = (
    "DictRepository",
    "Repository",
    "Resource",
    "SqlAlchemyRepository",
)

from lime_uow import exceptions

T = typing.TypeVar("T", covariant=True)
E = typing.TypeVar("E")


class Resource(abc.ABC, typing.Generic[T]):
    __resource_name__: typing.Optional[str] = None

    def __init__(self):
        if self.__resource_name__ is None:
            raise exceptions.ClassMissingResourceNameOverride(self.__class__.__name__)

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def open(self) -> Resource[T]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        if self.__resource_name__ is None:
            raise exceptions.ClassMissingResourceNameOverride(self.__class__.__name__)
        else:
            return self.__resource_name__

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


class Repository(Resource[E], abc.ABC, typing.Generic[E]):
    """Interface to access elements of a collection"""

    @abc.abstractmethod
    def add(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def all(self) -> typing.Iterable[E]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, item: E, /) -> E:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, item_id: typing.Any, /) -> E:
        raise NotImplementedError


class SqlAlchemyRepository(Repository[E], typing.Generic[E]):
    def __init__(
        self,
        entity: typing.Type[E],
        session: orm.Session,
    ):
        super().__init__()

        self._entity = entity
        self._session = session

        self.in_transaction = False

    def __enter__(self):
        return self.open()

    def __exit__(self, *args):
        return self.close()

    def close(self) -> None:
        self.in_transaction = False
        # self._session.close()

    def open(self) -> SqlAlchemyRepository[E]:
        self.in_transaction = True
        return self

    def rollback(self) -> None:
        if self.in_transaction:
            self._session.rollback()
        else:
            raise exceptions.MissingTransactionBlock(
                "Attempted to rollback a repository outside of a transaction."
            )

    def save(self) -> None:
        if self.in_transaction:
            self._session.commit()
        else:
            raise exceptions.MissingTransactionBlock(
                "Attempted to save a repository outside of a transaction."
            )

    def all(self) -> typing.Generator[E, None, None]:
        return self._session.query(self._entity).all()

    def add(self, item: E, /) -> E:
        if self.in_transaction:
            self._session.add(item)
            return item
        else:
            raise exceptions.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )

    def delete(self, item: E, /) -> E:
        if self.in_transaction:
            self._session.delete(item)
            return item
        else:
            raise exceptions.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )

    def update(self, item: E, /) -> E:
        if self.in_transaction:
            self._session.merge(item)
            return item
        else:
            raise exceptions.MissingTransactionBlock(
                "Attempted to edit repository outside of a transaction."
            )

    def get(self, item_id: typing.Any, /) -> E:
        return self._session.query(self._entity).get(item_id)

    def where(self, predicate: typing.Any, /) -> typing.List[E]:
        return self._session.query(self._entity).filter(predicate).all()


class DictRepository(Repository[E], typing.Generic[E]):
    """Repository implementation based on a dictionary

    This exists primarily to make testing in client code simpler.  It was not designed for efficiency.
    """

    def __init__(
        self,
        *,
        initial_values: typing.Dict[typing.Hashable, E],
        key_fn: typing.Callable[[E], typing.Hashable],
    ):
        super().__init__()

        self._previous_state = initial_values
        self._current_state = initial_values.copy()
        self._key_fn = key_fn

        self.events: typing.List[typing.Tuple[str, typing.Dict[str, typing.Any]]] = []

    def __enter__(self):
        return self.open()

    def __exit__(self, *args):
        self.rollback()
        return self.close()

    def close(self) -> None:
        self.events.append(("close", {}))
        self._current_state = {}

    def open(self) -> DictRepository[E]:
        self.events = [("open", {})]
        return self

    def rollback(self) -> None:
        self.events.append(("rollback", {}))
        self._current_state = self._previous_state.copy()

    def save(self) -> None:
        self.events.append(("save", {}))
        self._previous_state = self._current_state.copy()

    def add(self, item: E, /) -> E:
        self.events.append(("add", {"item": item}))
        key = self._key_fn(item)
        self._current_state[key] = item
        return item

    def all(self) -> typing.Iterable[E]:
        self.events.append(("all", {}))
        return list(self._current_state.values())

    def delete(self, item: E, /) -> E:
        self.events.append(("delete", {"item": item}))
        key = self._key_fn(item)
        del self._current_state[key]
        return item

    def update(self, item: E, /) -> E:
        self.events.append(("update", {"item": item}))
        key = self._key_fn(item)
        self._current_state[key] = item
        return item

    def get(self, item_id: typing.Any, /) -> E:
        self.events.append(("get", {"item_id": item_id}))
        return self._current_state[item_id]

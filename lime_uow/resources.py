from __future__ import annotations

import abc
import inspect
import os
import pathlib
import tempfile
import typing

from sqlalchemy import orm

__all__ = (
    "DummyRepository",
    "Repository",
    "Resource",
    "SharedResource",
    "SqlAlchemyRepository",
    "SqlAlchemySession",
    "TempFileSharedResource",
)

from lime_uow import exceptions

T = typing.TypeVar("T", covariant=True)
E = typing.TypeVar("E")


class Resource(abc.ABC, typing.Generic[T]):
    @classmethod
    def resource_name(cls) -> str:
        if inspect.isabstract(cls):
            return cls.__name__
        else:
            return _get_next_descendant_of(cls, ancestor=Resource).__name__

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
                self.resource_name
                == typing.cast(Resource[typing.Any], other).resource_name
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
        return hash(self.resource_name)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.__class__.resource_name()}"


class Repository(Resource[E], abc.ABC, typing.Generic[E]):
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


class SharedResource(Resource[T], abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def open(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError


class SqlAlchemyRepository(Repository[E], abc.ABC, typing.Generic[E]):
    def __init__(self, session: orm.Session, /):
        self._session = session
        self._entity_type: typing.Optional[typing.Type[E]] = None

    def add(self, item: E, /) -> E:
        self.session.add(item)
        return item

    def add_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        self.session.bulk_save_objects(items)
        return items

    def all(self) -> typing.Generator[E, None, None]:
        return self.session.query(self.entity_type).all()

    def delete(self, item: E, /) -> E:
        self.session.delete(item)
        return item

    def delete_all(self) -> None:
        self.session.query(self.entity_type).delete(synchronize_session=False)

    def get(self, item_id: typing.Any, /) -> E:
        return self.session.query(self.entity_type).get(item_id)

    @property
    @abc.abstractmethod
    def entity_type(self) -> typing.Type[E]:
        raise NotImplementedError

    def rollback(self) -> None:
        self.session.rollback()

    def save(self) -> None:
        self.session.commit()

    @property
    def session(self) -> orm.Session:
        return self._session

    def set_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        self.session.query(self.entity_type).delete()
        self.session.bulk_save_objects(items)
        return items

    def update(self, item: E, /) -> E:
        self.session.merge(item)
        return item

    def where(self, predicate: typing.Any, /) -> typing.List[E]:
        return self.session.query(self.entity_type).filter(predicate).all()


class DummyRepository(Repository[E], typing.Generic[E]):
    """Repository implementation based on a dictionary

    This exists primarily to make testing in client code simpler.  It was not designed for efficiency.
    """

    def __init__(
        self,
        *,
        key_fn: typing.Callable[[E], typing.Hashable],
        initial_values: typing.Optional[typing.Iterable[E]] = None,
    ):
        super().__init__()

        self._current_state: typing.List[E] = list(initial_values or [])
        self._previous_state: typing.List[E] = self._current_state.copy()
        self._key_fn = key_fn

        self.events: typing.List[typing.Tuple[str, typing.Dict[str, typing.Any]]] = []

    def rollback(self) -> None:
        self.events.append(("rollback", {}))
        self._current_state = self._previous_state.copy()

    def save(self) -> None:
        self.events.append(("save", {}))
        self._previous_state = self._current_state.copy()

    def add(self, item: E, /) -> E:
        self.events.append(("add", {"item": item}))
        self._current_state.append(item)
        return item

    def add_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        self.events.append(("add_all", {"items": items}))
        self._current_state += items
        return items

    def all(self) -> typing.Iterable[E]:
        self.events.append(("all", {}))
        return list(self._current_state)

    def delete(self, item: E, /) -> E:
        self.events.append(("delete", {"item": item}))
        self._current_state = [
            o for o in self._current_state if self._key_fn(item) != self._key_fn(o)
        ]
        return item

    def delete_all(self) -> None:
        self.events.append(("delete_all", {}))
        self._current_state = []

    def set_all(self, items: typing.Collection[E], /) -> typing.Collection[E]:
        self.events.append(("set_all", {"items": items}))
        self._current_state = list(items)
        return items

    def update(self, item: E, /) -> E:
        self.events.append(("update", {"item": item}))
        original_index = next(
            ix
            for ix, o in enumerate(self._current_state)
            if self._key_fn(item) == self._key_fn(o)
        )
        self._current_state[original_index] = item
        return item

    def get(self, item_id: typing.Any, /) -> E:
        self.events.append(("get", {"item_id": item_id}))
        return next(o for o in self._current_state if self._key_fn(o) == item_id)


class SqlAlchemySession(SharedResource[typing.Any]):
    def __init__(self, session_factory: orm.sessionmaker, /):
        self._session_factory = session_factory
        self._session: typing.Optional[orm.Session] = None

    def open(self) -> orm.Session:
        self._session = self._session_factory()
        return self._session

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def rollback(self) -> None:
        if self._session is None:
            raise exceptions.RollbackError(
                resource_name=self.resource_name(),
                message="Attempted to rollback a closed session.",
            )
        else:
            self._session.rollback()

    def save(self) -> None:
        if self._session:
            self._session.commit()


class TempFileSharedResource(SharedResource[typing.IO[bytes]]):
    def __init__(
        self,
        *,
        prefix: typing.Optional[str] = None,
        file_extension: typing.Optional[str] = None,
    ):
        self._prefix = prefix
        self._file_extension = file_extension

        self._file_handle: typing.Optional[typing.IO[bytes]] = None
        self._file_path: typing.Optional[pathlib.Path] = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def clear(self):
        self.handle.seek(0, 0)  # go to beginning of file
        self.handle.truncate()

    def close(self) -> None:
        self.handle.close()
        os.unlink(self.file_path)

    @property
    def handle(self) -> typing.IO[bytes]:
        if self._file_handle is None:
            self.open()
        return self._file_handle  # type: ignore

    @property
    def file_path(self) -> pathlib.Path:
        if self._file_path is None:
            self._file_path = pathlib.Path(self.handle.name)
        return self._file_path

    def open(self) -> typing.IO[bytes]:
        ext = f".{self._file_extension}" if self._file_extension else None
        self._file_handle = tempfile.NamedTemporaryFile(
            prefix=self._prefix,
            suffix=ext,
            delete=False,
        )
        return self._file_handle

    def all(self) -> str:
        self.handle.seek(0, 0)  # go to beginning of file
        content = self.handle.read()
        self.handle.seek(0, 2)  # go to end of file
        return content.decode()

    def rollback(self) -> None:
        pass

    def save(self) -> None:
        self.handle.flush()

    def add(self, content: str) -> None:
        self.handle.write(content.encode())


def _get_next_descendant_of(
    cls: typing.Type[typing.Any], ancestor: typing.Type[typing.Any]
) -> typing.Type[typing.Any]:
    try:
        return next(c for c in cls.__mro__[1:] if ancestor in c.__mro__)
    except StopIteration:
        raise exceptions.NoCommonAncestor(
            f"Cannot find a common ancestor of {ancestor.__name__} for class {cls.__name__} in its "
            f"MRO.  The {cls.__name__}'s MRO is as follows: "
            f"{', '.join(c.__name__ for c in cls.__mro__)}."
        )

import abc
import typing

from sqlalchemy import orm

__all__ = (
    "Resource",
    "SqlAlchemySessionResource",
)

from lime_uow import exception

T = typing.TypeVar("T", covariant=True)


class Resource(abc.ABC, typing.Generic[T]):
    @abc.abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def name(self) -> str:
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
            return self.name == typing.cast(Resource[T], other).name
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


class SqlAlchemySessionResource(Resource[orm.Session]):
    def __init__(self, name: str, session_factory: orm.sessionmaker):
        self._name = name
        self._session_factory = session_factory
        self._session: typing.Optional[orm.Session] = None

    def close(self) -> None:
        if self._session is None:
            raise exception.UninitializedSessionError()
        else:
            self._session.close()

    @property
    def name(self) -> str:
        return self._name

    def open(self) -> orm.Session:
        if self._session is None:
            self._session = self._session_factory()
        return self._session

    def rollback(self) -> None:
        if self._session is None:
            raise exception.UninitializedSessionError()
        else:
            self._session.rollback()

    def save(self) -> None:
        if self._session is None:
            raise exception.UninitializedSessionError()
        else:
            self._session.commit()

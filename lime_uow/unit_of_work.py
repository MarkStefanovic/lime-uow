from __future__ import annotations

import abc
import typing

from sqlalchemy import orm

from lime_uow import resources, exceptions

__all__ = (
    "SqlAlchemyUnitOfWork",
    "UnitOfWork",
)


R = typing.TypeVar("R", bound=resources.Resource[typing.Union[object, typing.Any]])  # hack around issue: https://github.com/python/mypy/issues/5374
# R = typing.TypeVar("R", bound=resources.Resource[typing.Any])


class UnitOfWork(abc.ABC):
    def __init__(self):
        self.__resources: typing.Optional[
            typing.Dict[str, resources.Resource[typing.Any]]
        ] = None
        self.__resources_validated = False

    def __enter__(self) -> UnitOfWork:
        rs: typing.AbstractSet[resources.Resource[typing.Any]] = self.create_resources()
        if not self.__resources_validated:
            _check_for_duplicate_resource_names(rs)
            self.__resources_validated = True
        self.__resources = {r.__class__.resource_name(): r for r in rs}
        return self

    def __exit__(self, *args):
        self.rollback()
        self.__resources = None

    def get_resource(self, resource_type: typing.Type[R], /) -> R:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            return typing.cast(R, self.get_resource_by_name(resource_type.resource_name()))

    def get_resource_by_name(self, resource_name: str, /) -> resources.Resource[typing.Any]:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            try:
                return self.__resources[resource_name]
            except KeyError:
                raise exceptions.MissingResourceError(
                    resource_name=resource_name,
                    available_resources=self.__resources.keys(),
                )

    @abc.abstractmethod
    def create_resources(self) -> typing.AbstractSet[resources.Resource[typing.Any]]:
        raise NotImplementedError

    def rollback(self):
        err_messages: typing.List[str] = []
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            for resource in self.__resources.values():
                try:
                    resource.rollback()
                except Exception as e:
                    err_messages.append(f"{resource.resource_name()}: {e}")

        if err_messages:
            err_msg_list = ", ".join(err_messages)
            err_msg = (
                f"The following errors occurred while performing a rollback on the"
                f" UnitOfWork: {err_msg_list}"
            )
            raise exceptions.RollbackError(err_msg)

    def save(self):
        # noinspection PyBroadException
        try:
            if self.__resources is None:
                raise exceptions.OutsideTransactionError()
            else:
                for resource in self.__resources.values():
                    resource.save()
        except:
            self.rollback()
            raise


def _check_for_duplicate_resource_names(rs: typing.Collection[R], /):
    names = [r.__class__.resource_name() for r in rs]
    duplicate_names = {name: ct for name in names if (ct := names.count(name)) > 1}
    if duplicate_names:
        raise exceptions.DuplicateResourceNames(duplicate_names)


class SqlAlchemyUnitOfWork(UnitOfWork, abc.ABC):
    def __init__(self, session_factory: orm.sessionmaker, /):
        super().__init__()
        self._session_factory = session_factory
        self._session: typing.Optional[orm.Session] = None

    @property
    def session(self) -> orm.Session:
        if self._session is None:
            raise exceptions.OutsideTransactionError()
        else:
            return self._session

    def __enter__(self) -> SqlAlchemyUnitOfWork:
        self._session = self._session_factory()
        return typing.cast(SqlAlchemyUnitOfWork, super().__enter__())

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.rollback()
        self.session.close()
        self._session = None

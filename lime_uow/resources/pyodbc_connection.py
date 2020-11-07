from __future__ import annotations

import typing

import pyodbc

from lime_uow import exceptions
from lime_uow.resources import resource

__all__ = ("PyodbcConnection",)


class PyodbcConnection(resource.Resource[pyodbc.Connection]):
    def __init__(
        self,
        db_uri: str,
        autocommit: bool = False,
        read_only: bool = False,
    ):
        self._db_uri = db_uri
        self._autocommit = autocommit
        self._read_only = read_only

        self._handle: typing.Optional[pyodbc.Connection] = None

    def open(self) -> pyodbc.Connection:
        if self._handle is None:
            self._handle = pyodbc.connect(
                self._db_uri,
                autocommit=self._autocommit,
                readonly=self._read_only,
            )
            self._handle.maxwrite = 1024 * 1024 * 1024
        return self._handle

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    @classmethod
    def interface(cls) -> typing.Type[PyodbcConnection]:
        return PyodbcConnection

    def rollback(self) -> None:
        if self._handle is not None:
            self._handle.rollback()

    def save(self) -> None:
        if self._read_only:
            raise exceptions.ReadOnlyConnection(
                "Attempted to call save() on a read-only connection."
            )
        if self._handle is None:
            raise exceptions.ResourceClosed()
        else:
            self._handle.commit()

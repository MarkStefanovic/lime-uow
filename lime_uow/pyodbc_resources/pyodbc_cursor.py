from __future__ import annotations

import typing

import pyodbc

from lime_uow.resources import resource

__all__ = ("PyodbcCursor",)


class PyodbcCursor(resource.Resource[pyodbc.Cursor]):
    def __init__(
        self,
        *,
        con: pyodbc.Connection,
        fast_executemany: bool = True,
    ):
        self._con = con
        self._fast_executemany = fast_executemany

        self._handle: typing.Optional[pyodbc.Cursor] = None

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def open(self) -> pyodbc.Cursor:
        if self._handle is None:
            self._handle = self._con.cursor()
            self._handle.fast_executemany = self._fast_executemany
            # self._handle.setinputsizes([(pyodbc.SQL_WVARCHAR, 0, 0)])
        return self._handle

    @classmethod
    def interface(cls) -> typing.Type[PyodbcCursor]:
        return PyodbcCursor

    def rollback(self) -> None:
        if self._handle is not None:
            self._handle.rollback()

    def save(self) -> None:
        if self._handle is not None:
            self._handle.commit()

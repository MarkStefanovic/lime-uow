from __future__ import annotations

import typing

import sqlalchemy as sa

from lime_uow.resources.resource import Resource

__all__ = ("SqlAlchemyTransaction",)


class SqlAlchemyTransaction(Resource[sa.engine.Transaction]):
    def __init__(self, /, engine: sa.engine.Engine):
        self._engine = engine
        self._transaction: typing.Optional[sa.engine.Transaction] = None

    def open(self) -> sa.engine.Transaction:
        if self._transaction is None:
            self._transaction = self._engine.begin()
        return self._transaction

    def close(self) -> None:
        if self._transaction is not None:
            self._transaction.close()
            self._transaction = None

    @classmethod
    def interface(cls) -> typing.Type[SqlAlchemyTransaction]:
        return SqlAlchemyTransaction

    def rollback(self) -> None:
        if self._transaction is not None:
            self._transaction.rollback()

    def save(self) -> None:
        if self._transaction is not None:
            self._transaction.commit()

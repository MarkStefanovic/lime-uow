from __future__ import annotations

import typing

import sqlalchemy as sa

from lime_uow.resources import resource
from lime_uow.sqlalchemy_resources import sqlalchemy_transaction

__all__ = ("SqlAlchemyEngine",)


class SqlAlchemyEngine(resource.Resource[sa.engine.Engine]):
    def __init__(self, /, db_uri: str):
        self._db_uri = db_uri
        self._engine: typing.Optional[sa.engine.Engine] = None

    def transaction(self) -> sqlalchemy_transaction.SqlAlchemyTransaction:
        return sqlalchemy_transaction.SqlAlchemyTransaction(self._engine)

    def open(self) -> sa.engine.Engine:
        if self._engine is None:
            self._engine = sa.create_engine(self._db_uri)
        return self._engine

    @classmethod
    def interface(cls) -> typing.Type[SqlAlchemyEngine]:
        return SqlAlchemyEngine

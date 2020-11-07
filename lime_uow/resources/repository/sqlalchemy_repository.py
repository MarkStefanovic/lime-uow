import abc
import typing

from sqlalchemy import orm

from lime_uow.resources.repository import repository

E = typing.TypeVar("E")

__all__ = ("SqlAlchemyRepository",)


class SqlAlchemyRepository(repository.Repository[E], abc.ABC, typing.Generic[E]):
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

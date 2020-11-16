import abc
import typing

from sqlalchemy import orm

from lime_uow.resources import repository

EntityType = typing.TypeVar("EntityType")

__all__ = ("SqlAlchemyRepository",)


class SqlAlchemyRepository(
    repository.Repository[EntityType], abc.ABC, typing.Generic[EntityType]
):
    def __init__(self, session: orm.Session, /):
        self._session = session
        self._entity_type: typing.Optional[typing.Type[EntityType]] = None

    def add(self, item: EntityType, /) -> EntityType:
        self.session.add(item)
        return item

    def add_all(
        self, items: typing.Collection[EntityType], /
    ) -> typing.Collection[EntityType]:
        self.session.bulk_save_objects(items)
        return items

    def all(self) -> typing.Generator[EntityType, None, None]:
        return self.session.query(self.entity_type).all()

    def delete(self, item: EntityType, /) -> EntityType:
        self.session.delete(item)
        return item

    def delete_all(self) -> None:
        self.session.query(self.entity_type).delete(synchronize_session=False)

    def get(self, item_id: typing.Any, /) -> EntityType:
        return self.session.query(self.entity_type).get(item_id)

    @property
    @abc.abstractmethod
    def entity_type(self) -> typing.Type[EntityType]:
        raise NotImplementedError

    def rollback(self) -> None:
        self.session.rollback()

    def save(self) -> None:
        self.session.commit()

    @property
    def session(self) -> orm.Session:
        return self._session

    def set_all(
        self, items: typing.Collection[EntityType], /
    ) -> typing.Collection[EntityType]:
        self.session.query(self.entity_type).delete()
        self.session.bulk_save_objects(items)
        return items

    def update(self, item: EntityType, /) -> EntityType:
        self.session.merge(item)
        return item

    def where(self, predicate: typing.Any, /) -> typing.List[EntityType]:
        return self.session.query(self.entity_type).filter(predicate).all()

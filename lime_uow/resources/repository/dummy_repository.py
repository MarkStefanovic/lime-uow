import abc
import typing

from lime_uow.resources.repository import repository

E = typing.TypeVar("E")

__all__ = ("DummyRepository",)


class DummyRepository(repository.Repository[E], abc.ABC, typing.Generic[E]):
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

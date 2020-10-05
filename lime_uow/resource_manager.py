import typing

from lime_uow.resrc import Resource

__all__ = ("ResourceManager",)

T = typing.TypeVar("T", covariant=True)


class ResourceManager(typing.Generic[T]):
    def __init__(self, resource: Resource[T], /):
        if resource is None:
            raise ValueError(
                f"Expected a resource with a close and open method, but got None."
            )

        if not hasattr(resource, "open") or not hasattr(resource, "close"):
            raise ValueError(
                f"Expected a resource with a close and open method, but got {resource!r}."
            )

        self._handle: typing.Optional[T] = None
        self._resource: Resource[T] = resource

    def close(self) -> bool:
        if self._handle is None:
            return False
        else:
            self._resource.close()
            self._handle = None
            return True

    @property
    def is_open(self) -> bool:
        return self._handle is not None

    def open(self) -> T:
        if self._handle is None:
            self._handle = self._resource.open()
        return self._handle

    def rollback(self) -> None:
        return self._resource.rollback()

    def save(self) -> None:
        return self._resource.save()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._resource!r})"

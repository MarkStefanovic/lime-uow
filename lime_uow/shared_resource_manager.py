from __future__ import annotations

import typing

from lime_uow import exceptions, resources

__all__ = (
    "SharedResources",
    "PlaceholderSharedResources",
)

T = typing.TypeVar("T")


class SharedResources:
    def __init__(self, /, *shared_resource: resources.Resource[typing.Any]):
        resources.check_for_ambiguous_implementations(shared_resource)
        self.__shared_resources = tuple(shared_resource)
        self.__handles: typing.Dict[str, typing.Any] = {}
        self.__opened = False
        self.__closed = False

    def __enter__(self) -> SharedResources:
        if self.__opened:
            raise exceptions.ResourcesAlreadyOpen()
        if self.__closed:
            raise exceptions.ResourceClosed()
        self.__opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self):
        if self.__closed:
            raise exceptions.ResourceClosed()
        for resource in self.__shared_resources:
            resource.close()
        self.__handles = {}
        self.__closed = True
        self.__opened = False

    def get(
        self,
        resource_type: typing.Type[resources.Resource[T]],
    ) -> T:
        if self.__closed:
            raise exceptions.ResourceClosed()
        if resource_type.interface() in self.__handles.keys():
            return self.__handles[resource_type.interface().__name__]
        else:
            try:
                resource = next(
                    resource
                    for resource in self.__shared_resources
                    if resource.interface() == resource_type.interface()
                )
                handle = resource.open()
                self.__handles[resource.interface().__name__] = handle
                return handle
            except StopIteration:
                raise exceptions.MissingResourceError(
                    resource_name=resource_type.interface().__name__,
                    available_resources={
                        r.interface().__name__ for r in self.__shared_resources
                    },
                )
            except Exception as e:
                raise exceptions.LimeUoWException(str(e))

    def __eq__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            # noinspection PyTypeChecker
            return (
                self.__shared_resources
                == typing.cast(SharedResources, other).__shared_resources
            )
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__shared_resources)

    def __repr__(self) -> str:
        resources_str = ", ".join(
            r.interface().__name__ for r in self.__shared_resources
        )
        return f"{self.__class__.__name__}: {resources_str}"


class PlaceholderSharedResources(SharedResources):
    def __init__(self):
        super().__init__()

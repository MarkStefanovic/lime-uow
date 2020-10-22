from __future__ import annotations

import typing

from lime_uow import exceptions, resources

__all__ = (
    "SharedResources",
    "PlaceholderSharedResources",
)

T = typing.TypeVar("T")


class SharedResources:
    def __init__(self, /, *shared_resource: resources.SharedResource[typing.Any]):
        resources.check_for_ambiguous_implementations(shared_resource)
        self.__shared_resources = list(shared_resource)
        self.__handles: typing.Dict[str, typing.Any] = {}
        self.__opened = False
        self.__closed = False

    def __enter__(self) -> SharedResources:
        if self.__opened:
            raise exceptions.SharedResourcesAlreadyOpen()
        if self.__closed:
            raise exceptions.SharedResourcesClosed()
        self.__opened = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self):
        if self.__closed:
            raise exceptions.SharedResourcesClosed()
        for resource in self.__shared_resources:
            resource.close()
        self.__shared_resources = []
        self.__handles = {}
        self.__closed = True
        self.__opened = False

    def get(self, shared_resource_type: typing.Type[resources.SharedResource[T]]) -> T:
        if self.__closed:
            raise exceptions.SharedResourcesClosed()
        if shared_resource_type.interface() in self.__handles.keys():
            return self.__handles[shared_resource_type.interface().__name__]
        else:
            try:
                resource = next(
                    resource
                    for resource in self.__shared_resources
                    if resource.interface() == shared_resource_type.interface()
                )
                handle = resource.open()
                self.__handles[resource.interface().__name__] = handle
                return handle
            except StopIteration:
                raise exceptions.MissingResourceError(
                    resource_name=shared_resource_type.interface().__name__,
                    available_resources={
                        r.interface().__name__ for r in self.__shared_resources
                    },
                )
            except Exception as e:
                raise exceptions.LimeUoWException(str(e))


class PlaceholderSharedResources(SharedResources):
    def __init__(self):
        super().__init__()

from __future__ import annotations

import typing

from lime_uow import resources, exceptions

__all__ = ("UnitOfWork",)


T = typing.TypeVar("T", bound=resources.Resource[typing.Any])


class UnitOfWork:
    def __init__(self, /, *resource: resources.Resource[typing.Any]):
        names = [r.resource_name() for r in resource]
        duplicate_names = {name: ct for name in names if (ct := names.count(name)) > 1}
        if duplicate_names:
            raise exceptions.DuplicateResourceNames(duplicate_names)

        self._resources = {r.resource_name(): r for r in resource}

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()
        for resource in self._resources.values():
            resource.close()

    def get_resource(self, resource_type: typing.Type[T], /) -> T:
        return self.get_resource_by_name(resource_type.resource_name())

    def get_resource_by_name(self, resource_name: str) -> typing.Any:
        try:
            return self._resources[resource_name]
        except KeyError:
            raise exceptions.MissingResourceError(resource_name)

    def rollback(self):
        err_messages: typing.List[str] = []
        for resource in self._resources.values():
            if resource.is_open:
                try:
                    resource.rollback()
                except Exception as e:
                    err_messages.append(f"{resource.name}: {e}")

        if err_messages:
            err_msg_list = ", ".join(err_messages)
            err_msg = (
                f"The following errors occurred while performing a rollback on the"
                f" UnitOfWork: {err_msg_list}"
            )
            raise exceptions.RollbackError(err_msg)

    def save(self):
        # noinspection PyBroadException
        try:
            for resource in self._resources.values():
                if resource.is_open:
                    resource.save()
        except:
            self.rollback()
            raise

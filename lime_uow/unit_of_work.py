from __future__ import annotations

import typing

from lime_uow import Resource, exception, resource_manager

__all__ = ("UnitOfWork",)


class UnitOfWork:
    def __init__(self, /, *resources: Resource[typing.Any]):
        names = [resource.name for resource in resources]
        duplicate_names = {name: ct for name in names if (ct := names.count(name)) > 1}
        if duplicate_names:
            raise exception.DuplicateResourceNames(duplicate_names)

        self._resource_managers = {
            resource.name: resource_manager.ResourceManager(resource)
            for resource in resources
        }
        self._activated = False

    def __enter__(self) -> UnitOfWork:
        if self._activated:
            raise exception.NestingUnitsOfWorkNotAllowed()

        self._activated = True
        return self

    def __exit__(self, *args):
        self.rollback()
        for resource in self._resource_managers.values():
            resource.close()
        self._activated = False

    def get_resource(self, resource_name: str) -> typing.Any:
        if not self._activated:
            raise exception.MissingTransactionBlock(
                "Attempted access a resource managed by a UnitOfWork instance outside a `with` block."
            )

        try:
            mgr = self._resource_managers[resource_name]
        except IndexError:
            raise exception.MissingResourceError(resource_name)

        return mgr.open()

    def rollback(self):
        if not self._activated:
            raise exception.MissingTransactionBlock(
                "Attempted to rollback a UnitOfWork instance outside a `with` block."
            )

        err_messages: typing.List[str] = []
        for resource in self._resource_managers.values():
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
            raise exception.RollbackError(err_msg)

    def save(self):
        if not self._activated:
            raise exception.MissingTransactionBlock(
                "Attempted to save a UnitOfWork instance outside a `with` block."
            )

        # noinspection PyBroadException
        try:
            for resource in self._resource_managers.values():
                if resource.is_open:
                    resource.save()
        except:
            self.rollback()
            raise

from __future__ import annotations

import typing

from lime_uow import Resource, exception, resource_manager


class UnitOfWork:
    def __init__(self, /, *resources: Resource[typing.Any]):
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
            raise exception.OutsideUnitOfWorkContext()
        try:
            mgr = self._resource_managers[resource_name]
        except IndexError:
            raise exception.MissingResourceError(resource_name)
        return mgr.open()

    def rollback(self):
        if not self._activated:
            raise exception.OutsideUnitOfWorkContext()

        for resource in self._resource_managers.values():
            if resource.is_open:
                resource.rollback()

    def save(self):
        if not self._activated:
            raise exception.OutsideUnitOfWorkContext()

        # noinspection PyBroadException
        try:
            for resource in self._resource_managers.values():
                if resource.is_open:
                    resource.save()
        except:
            self.rollback()
            raise

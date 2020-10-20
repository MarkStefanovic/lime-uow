from __future__ import annotations

import abc
import typing

from lime_uow import exceptions, resources, shared_resource_manager

__all__ = (
    "PlaceholderUnitOfWork",
    "UnitOfWork",
)


R = typing.TypeVar("R", bound=resources.Resource[typing.Any])
T = typing.TypeVar("T")


class UnitOfWork(abc.ABC):
    def __init__(
        self,
        /,
        shared_resources: shared_resource_manager.SharedResources = shared_resource_manager.PlaceholderSharedResources(),
    ):
        self.__resources: typing.Optional[
            typing.Set[resources.Resource[typing.Any]]
        ] = None
        self.__shared_resource_manager = shared_resources
        self.__resources_validated = False

    def __enter__(self) -> UnitOfWork:
        fresh_resources = self.create_resources(self.__shared_resource_manager)
        resources.check_for_duplicate_resource_names(fresh_resources)
        self.__resources = set(fresh_resources)
        self.__resources_validated = True
        return self

    def __exit__(self, *args):
        errors: typing.List[exceptions.RollbackError] = []
        try:
            self.rollback()
        except exceptions.RollbackErrors as e:
            errors += e.rollback_errors
        self.__resources = None
        if errors:
            raise exceptions.RollbackErrors(*errors)

    def get_resource(self, resource_type: typing.Type[R], /) -> R:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            return typing.cast(
                R, self.get_resource_by_name(resource_type.resource_name())
            )

    def get_resource_by_name(
        self, resource_name: str, /
    ) -> resources.Resource[typing.Any]:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            try:
                return next(
                    resource
                    for resource in self.__resources
                    if resource.resource_name() == resource_name
                )
            except StopIteration:
                raise exceptions.MissingResourceError(
                    resource_name=resource_name,
                    available_resources={r.resource_name() for r in self.__resources},
                )

    @abc.abstractmethod
    def create_resources(
        self, shared_resources: shared_resource_manager.SharedResources
    ) -> typing.Iterable[resources.Resource[typing.Any]]:
        raise NotImplementedError

    def rollback(self):
        errors: typing.List[exceptions.RollbackError] = []
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            for resource in self.__resources:
                try:
                    resource.rollback()
                except Exception as e:
                    errors.append(
                        exceptions.RollbackError(
                            resource_name=resource.resource_name(),
                            message=str(e),
                        )
                    )

        if errors:
            raise exceptions.RollbackErrors(*errors)

    def save(self):
        # noinspection PyBroadException
        try:
            if self.__resources is None:
                raise exceptions.OutsideTransactionError()
            else:
                for resource in self.__resources:
                    resource.save()
        except:
            self.rollback()
            raise


class PlaceholderUnitOfWork(UnitOfWork):
    def __init__(self):
        super().__init__(shared_resource_manager.PlaceholderSharedResources())

    def create_resources(
        self, shared_resources: shared_resource_manager.SharedResources
    ) -> typing.List[resources.Resource[typing.Any]]:
        return []

from __future__ import annotations

import abc
import inspect
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
        resources.check_for_ambiguous_implementations(fresh_resources)
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
            if inspect.isabstract(resource_type):
                interface_name = resource_type.__name__
            else:
                interface_name = resource_type.interface().__name__
            implementation = next(
                resource
                for resource in self.__resources
                if resource.interface().__name__ == interface_name
            )
            return typing.cast(R, implementation)

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
                            message=f"An error occurred while rolling back {self.__class__.__name__}: {e}",
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

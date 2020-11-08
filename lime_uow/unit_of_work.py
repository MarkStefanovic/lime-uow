from __future__ import annotations

import abc
import typing

from lime_uow import exceptions, resources, shared_resource_manager

__all__ = (
    "PlaceholderUnitOfWork",
    "UnitOfWork",
)


R = typing.TypeVar("R", bound=resources.Resource[typing.Any])
# noinspection PyTypeChecker
T = typing.TypeVar("T", bound="UnitOfWork")


class UnitOfWork(abc.ABC):
    def __init__(
        self,
        /,
        shared_resources: shared_resource_manager.SharedResources = shared_resource_manager.PlaceholderSharedResources(),
    ):
        self.__resources: typing.Optional[
            typing.Dict[str, resources.Resource[typing.Any]]
        ] = None
        self.__shared_resource_manager = shared_resources
        self.__resources_validated = False

    def __enter__(self: T) -> T:
        fresh_resources = self.create_resources(self.__shared_resource_manager)
        resources.check_for_ambiguous_implementations(fresh_resources)
        self.__resources = {
            resource.interface().__name__: resource for resource in fresh_resources
        }
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

    def exists(self, /, resource_type: typing.Type[R]) -> bool:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            return resource_type.__name__ in self.__resources.keys()

    def get(self, /, resource_type: typing.Type[R]) -> R:
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            if self.__shared_resource_manager.exists(resource_type):
                return typing.cast(R, self.__shared_resource_manager.get(resource_type))
            elif (interface_name := resource_type.__name__) in self.__resources.keys():
                return typing.cast(R, self.__resources[interface_name])
            else:
                raise exceptions.MissingResourceError(
                    resource_name=interface_name,
                    available_resources=self.__resources.keys(),
                )

    @abc.abstractmethod
    def create_resources(
        self, /, shared_resources: shared_resource_manager.SharedResources
    ) -> typing.Iterable[resources.Resource[typing.Any]]:
        raise NotImplementedError

    def rollback(self):
        errors: typing.List[exceptions.RollbackError] = []
        if self.__resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            for resource in self.__resources.values():
                try:
                    resource.rollback()
                except Exception as e:
                    errors.append(
                        exceptions.RollbackError(
                            f"An error occurred while rolling back {self.__class__.__name__}: {e}",
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
                for resource in self.__resources.values():
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

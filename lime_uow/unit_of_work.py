from __future__ import annotations

import abc
import typing


from lime_uow import resources, exceptions

__all__ = (
    "SharedResources",
    "UnitOfWork",
)


R = typing.TypeVar("R", bound=resources.Resource[typing.Any])
T = typing.TypeVar("T")


class UnitOfWork(abc.ABC):
    def __init__(self):
        self._resources: typing.Optional[
            typing.Set[resources.Resource[typing.Any]]
        ] = None
        self.__shared_resources: typing.Optional[SharedResources] = None
        self.__resources_validated = False

    def __enter__(self) -> UnitOfWork:
        self.__shared_resources = SharedResources(*self.create_shared_resources())
        fresh_resources = self.create_resources(self.__shared_resources)
        _check_for_duplicate_resource_names(fresh_resources)
        self._resources = set(fresh_resources)
        self.__resources_validated = True
        return self

    def __exit__(self, *args):
        errors: typing.List[exceptions.RollbackError] = []
        try:
            self.rollback()
        except exceptions.RollbackErrors as e:
            errors += e.rollback_errors
        self._resources = None
        assert self.__shared_resources is not None
        self.__shared_resources.close()
        self.__shared_resources = None
        if errors:
            raise exceptions.RollbackErrors(*errors)

    def get_resource(self, resource_type: typing.Type[R], /) -> R:
        if self._resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            return typing.cast(
                R, self.get_resource_by_name(resource_type.resource_name())
            )

    def get_resource_by_name(
        self, resource_name: str, /
    ) -> resources.Resource[typing.Any]:
        if self._resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            try:
                return next(
                    resource
                    for resource in self._resources
                    if resource.resource_name() == resource_name
                )
            except StopIteration:
                raise exceptions.MissingResourceError(
                    resource_name=resource_name,
                    available_resources={r.resource_name() for r in self._resources},
                )

    @abc.abstractmethod
    def create_resources(
        self, shared_resources: SharedResources
    ) -> typing.Iterable[resources.Resource[typing.Any]]:
        raise NotImplementedError

    @abc.abstractmethod
    def create_shared_resources(
        self,
    ) -> typing.Iterable[resources.SharedResource[typing.Any]]:
        raise NotImplementedError

    def rollback(self):
        errors: typing.List[exceptions.RollbackError] = []
        if self._resources is None:
            raise exceptions.OutsideTransactionError()
        else:
            for resource in self._resources:
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
            if self._resources is None:
                raise exceptions.OutsideTransactionError()
            else:
                for resource in self._resources:
                    resource.save()
        except:
            self.rollback()
            raise


class SharedResources:
    def __init__(self, /, *shared_resource: resources.SharedResource[typing.Any]):
        _check_for_duplicate_resource_names(shared_resource)
        self._shared_resources = list(shared_resource)
        self._handles: typing.Dict[str, typing.Any] = {}

    def close(self):
        for resource in self._shared_resources:
            resource.close()
        self._shared_resources = []
        self._handles = {}

    def get(self, shared_resource_type: typing.Type[resources.SharedResource[T]]) -> T:
        if shared_resource_type.resource_name() in self._handles.keys():
            return self._handles[shared_resource_type.resource_name()]
        else:
            try:
                resource = next(
                    resource
                    for resource in self._shared_resources
                    if resource.resource_name() == shared_resource_type.resource_name()
                )
                handle = resource.open()
                self._handles[resource.resource_name()] = handle
                return handle
            except StopIteration:
                raise exceptions.MissingResourceError(
                    resource_name=shared_resource_type.resource_name(),
                    available_resources={
                        r.resource_name() for r in self._shared_resources
                    },
                )
            except Exception as e:
                raise exceptions.LimeUoWException(str(e))


def _check_for_duplicate_resource_names(rs: typing.Iterable[R], /):
    names = [r.__class__.resource_name() for r in rs]
    duplicate_names = {name: ct for name in names if (ct := names.count(name)) > 1}
    if duplicate_names:
        raise exceptions.DuplicateResourceNames(duplicate_names)

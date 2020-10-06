import typing

__all__ = (
    "LimeUOW",
    "DuplicateResourceNames",
    "InvalidResource",
    "MissingResourceError",
    "MissingTransactionBlock",
    "NestingUnitsOfWorkNotAllowed",
    "RollbackError",
)


class LimeUOW(Exception):
    """Base class for exceptions arising from the lime-uow package"""

    def __init__(self, message: str, /):
        self.message = message
        super().__init__(message)


class DuplicateResourceNames(LimeUOW):
    def __init__(self, duplicates: typing.Mapping[str, int], /):
        self.duplicates = duplicates

        examples = ", ".join(
            f"{name} = {ct}" for name, ct in sorted(duplicates.items())
        )
        msg = f"Resource names must be unique, but found the following duplicates: {examples}."
        super().__init__(msg)


class InvalidResource(LimeUOW):
    def __init__(self, message: str, /):
        super().__init__(message)


class MissingResourceError(LimeUOW):
    def __init__(self, resource_name: str, /):
        self.resource_name = resource_name
        msg = f"Could not locate the resource named {resource_name}"
        super().__init__(msg)


class NestingUnitsOfWorkNotAllowed(LimeUOW):
    def __init__(self):
        super().__init__(
            "Attempted to nest a UnitOfWork instance inside another.  That is not supported."
        )


class MissingTransactionBlock(LimeUOW):
    def __init__(self, message: str):
        super().__init__(message)


class RollbackError(LimeUOW):
    def __init__(self, message: str, /):
        super().__init__(message)

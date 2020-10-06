__all__ = (
    "HealthNutApiException",
    "InvalidResource",
    "MissingResourceError",
    "MissingTransactionBlock",
    "NestingUnitsOfWorkNotAllowed",
    "RollbackError",
)


class HealthNutApiException(Exception):
    """Base class for excptions arising from the healthnut-api codebase"""

    def __init__(self, message: str, /):
        self.message = message
        super().__init__(message)


class InvalidResource(HealthNutApiException):
    def __init__(self, message: str, /):
        super().__init__(message)


class MissingResourceError(HealthNutApiException):
    def __init__(self, resource_name: str, /):
        self.resource_name = resource_name
        msg = f"Could not locate the resource named {resource_name}"
        super().__init__(msg)


class NestingUnitsOfWorkNotAllowed(HealthNutApiException):
    def __init__(self):
        super().__init__(
            "Attempted to nest a UnitOfWork instance inside another.  That is not supported."
        )


class MissingTransactionBlock(HealthNutApiException):
    def __init__(self, message: str):
        super().__init__(message)


class RollbackError(HealthNutApiException):
    def __init__(self, message: str, /):
        super().__init__(message)

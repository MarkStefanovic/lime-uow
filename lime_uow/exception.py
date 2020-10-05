__all__ = (
    "HealthNutApiException",
    "MissingResourceError",
    "NestingUnitsOfWorkNotAllowed",
    "OutsideUnitOfWorkContext",
    "UninitializedSessionError",
)


class HealthNutApiException(Exception):
    """Base class for excptions arising from the healthnut-api codebase"""

    def __init__(self, message: str, /):
        self.message = message
        super().__init__(message)


class MissingResourceError(HealthNutApiException):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name
        msg = f"Could not locate the resource named {resource_name}"
        super().__init__(msg)


class NestingUnitsOfWorkNotAllowed(HealthNutApiException):
    def __init__(self):
        super().__init__(
            "Attempted to nest a UnitOfWork instance inside another.  That is not supported."
        )


class OutsideUnitOfWorkContext(HealthNutApiException):
    def __init__(self):
        super().__init__(
            "Attempted to use a UnitOfWork instance outside a `with` block."
        )


class UninitializedSessionError(HealthNutApiException):
    def __init__(self):
        super().__init__("Attempted to use a session that has not been opened yet.")

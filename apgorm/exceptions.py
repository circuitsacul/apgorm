from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable, Type

if TYPE_CHECKING:  # pragma: no cover
    from .field import BaseField
    from .model import Model


class ApgormBaseException(Exception):
    """The base clase for all exceptions in apgorm."""

    __slots__: Iterable[str] = ()


# migration-side exceptions
class MigrationException(ApgormBaseException):
    """Base class for all exceptions related to migrations."""

    __slots__: Iterable[str] = ()


class NoMigrationsToCreate(MigrationException):
    """The migration for the given id was not found."""

    __slots__: Iterable[str] = ()

    def __init__(self) -> None:
        super().__init__("There are no migrations to create.")


class MigrationAlreadyApplied(MigrationException):
    """The migration has already been applied."""

    __slots__: Iterable[str] = ()

    def __init__(self, path: str) -> None:
        super().__init__(f"The migration at {path} has already been applied.")


# apgorm-side exceptions
class ApgormException(ApgormBaseException):
    """Base class for all exceptions related to the code of apgorm."""

    __slots__: Iterable[str] = ()


class UndefinedFieldValue(ApgormException):
    """Raised if you try to get the value for a field that is undefined.

    Usually means that the model has not been created."""

    __slots__: Iterable[str] = ("field",)

    def __init__(self, field: BaseField[Any, Any, Any]) -> None:
        self.field = field

        super().__init__(
            f"The field {field.full_name} is undefined. "
            "This usually means that the model has not been "
            "created."
        )


class InvalidFieldValue(ApgormException):
    """The field value failed the validator check."""

    __slots__: Iterable[str] = ()

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


class SpecifiedPrimaryKey(ApgormException):
    """You tried to create a primary key constraint by using PrimaryKey
    instead of Model.primary_key."""

    __slots__: Iterable[str] = ()

    def __init__(self, cls: str, fields: Iterable[str]) -> None:
        super().__init__(
            f"You tried to specify a primary key on {cls} by using "
            f"the PrimaryKey constraint. Please use {cls}.primary_key "
            "instead:\nprimary_key = ({},)".format(", ".join(fields))
        )


class BadArgument(ApgormException):
    """Bad arguments were passed."""

    __slots__: Iterable[str] = ("message",)

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


# postgres-side exceptions
class SqlException(ApgormBaseException):
    """Base class for all exceptions related to SQL."""

    __slots__: Iterable[str] = ()


class ModelNotFound(SqlException):
    """A model for the given parameters was not found."""

    __slots__: Iterable[str] = ("model", "value")

    def __init__(self, model: Type[Model], values: dict[str, Any]) -> None:
        self.model = model
        self.values = values

        super().__init__(
            "No Model was found for the following parameters:\n - "
            + ("\n - ".join(f"{k!r} = {v!r}" for k, v in values.items()))
        )

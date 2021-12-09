from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from .field import Field
    from .model import Model


class ApgormBaseException(Exception):
    """The base clase for all exceptions in apgorm."""


# migration-side exceptions
class MigrationException(ApgormBaseException):
    """Base class for all exceptions related to migrations."""


# apgorm-side exceptions
class ApgormException(ApgormBaseException):
    """Base class for all exceptions related to the code of apgorm."""


class UndefinedFieldValue(ApgormException):
    """Raised when try to get the value for a field that is undefined.

    Usually means that the model has not been fetched, saved, or created."""

    def __init__(self, field: Field):
        self.field = field

        super().__init__(
            f"The field {field.full_name} is undefined. "
            "This usually means that the model has not been "
            "fetched, created, or saved."
        )


class ReadOnlyField(ApgormException):
    """The field is read-only (you can't change its value)."""

    def __init__(self, field: Field):
        self.field = field

        super().__init__(f"The field {field.full_name} is read-only.")


# postgres-side exceptions
class SqlException(ApgormBaseException):
    """Base class for all exceptions related to SQL."""


class ModelNotFound(SqlException):
    """A model for the given parameters was not found."""

    def __init__(self, model: Type[Model], values: dict[str, Any]):
        self.model = model
        self.values = values

        super().__init__(
            "No Model was found for the following parameters:\n"
            " - "
            + ("\n - ".join([f"{k!r} = {v!r}" for k, v in values.items()]))
        )

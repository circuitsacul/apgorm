# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence, Type

if TYPE_CHECKING:  # pragma: no cover
    from .field import BaseField
    from .model import Model


class ApgormBaseException(Exception):
    """The base clase for all exceptions in apgorm."""


# migration-side exceptions
class MigrationException(ApgormBaseException):
    """Base class for all exceptions related to migrations."""


class NoMigrationsToCreate(MigrationException):
    """The migration for the given id was not found."""

    def __init__(self) -> None:
        super().__init__("There are no migrations to create.")


class MigrationAlreadyApplied(MigrationException):
    """The migration has already been applied."""

    def __init__(self, path: str) -> None:
        super().__init__(f"The migration at {path} has already been applied.")


# apgorm-side exceptions
class ApgormException(ApgormBaseException):
    """Base class for all exceptions related to the code of apgorm."""


class UndefinedFieldValue(ApgormException):
    """Raised if you try to get the value for a field that is undefined.

    Usually means that the model has not been created."""

    def __init__(self, field: BaseField) -> None:
        self.field = field

        super().__init__(
            f"The field {field.full_name} is undefined. "
            "This usually means that the model has not been "
            "created."
        )


class InvalidFieldValue(ApgormException):
    """The field value failed the validator check."""

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


class SpecifiedPrimaryKey(ApgormException):
    """You tried to create a primary key constraint by using PrimaryKey
    instead of Model.primary_key."""

    def __init__(self, cls: str, fields: Sequence[str]) -> None:
        super().__init__(
            f"You tried to specify a primary key on {cls} by using "
            f"the PrimaryKey constraint. Please use {cls}.primary_key "
            "instead:\nprimary_key = ({},)".format(", ".join(fields))
        )


class BadArgument(ApgormException):
    """Bad arguments were passed."""

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


# postgres-side exceptions
class SqlException(ApgormBaseException):
    """Base class for all exceptions related to SQL."""


class ModelNotFound(SqlException):
    """A model for the given parameters was not found."""

    def __init__(self, model: Type[Model], values: dict[str, Any]) -> None:
        self.model = model
        self.values = values

        super().__init__(
            "No Model was found for the following parameters:\n"
            " - "
            + ("\n - ".join([f"{k!r} = {v!r}" for k, v in values.items()]))
        )

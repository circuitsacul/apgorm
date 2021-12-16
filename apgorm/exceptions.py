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
    """Raised if you try to get the value for a field that is undefined.

    Usually means that the model has not been created."""

    def __init__(self, field: Field):
        self.field = field

        super().__init__(
            f"The field {field.full_name} is undefined. "
            "This usually means that the model has not been "
            "created."
        )


class ReadOnlyField(ApgormException):
    """The field is read-only (you can't change its value)."""

    def __init__(self, field: Field):
        self.field = field

        super().__init__(f"The field {field.full_name} is read-only.")


class BadArgument(ApgormException):
    """Bad arguments were passed."""

    def __init__(self, message: str):
        self.messages = message

        super().__init__(message)


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

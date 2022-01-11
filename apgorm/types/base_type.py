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

from typing import Callable, Generic, TypeVar

from apgorm.field import Field
from apgorm.undefined import UNDEF

_T = TypeVar("_T", covariant=True)
_S = TypeVar("_S", bound="SqlType", covariant=True)


class SqlType(Generic[_T]):
    """Base type for all SQL types."""

    _sql: str
    """The raw sql for the type."""

    def field(
        self: _S,
        default: _T | UNDEF = UNDEF.UNDEF,
        default_factory: Callable[[], _T] | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T]:
        """Generate a field using this type."""

        return Field(
            sql_type=self,
            default=default,
            default_factory=default_factory,
            not_null=True,
            use_repr=use_repr,
        )

    def nullablefield(
        self: _S,
        default: _T | None | UNDEF = UNDEF.UNDEF,
        default_factory: Callable[[], _T] | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T | None]:
        """Generate a nullable field using this type."""

        return Field(
            sql_type=self,
            default=default,
            default_factory=default_factory,
            not_null=False,
            use_repr=use_repr,
        )

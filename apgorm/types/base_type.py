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

from typing import TYPE_CHECKING, Generic, TypeVar

from apgorm.field import Field

if TYPE_CHECKING:
    from apgorm.field import BaseField

_T = TypeVar("_T", covariant=True)
_S = TypeVar("_S", bound="SqlType", covariant=True)


class SqlType(Generic[_T]):
    sql: str

    def field(
        self: _S,
        default: str | BaseField | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T]:
        return Field(
            sql_type=self,
            default=default,
            not_null=True,
            use_repr=use_repr,
        )

    def nullablefield(
        self: _S,
        default: str | BaseField | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T | None]:
        return Field(
            sql_type=self,
            default=default,
            not_null=False,
            use_repr=use_repr,
        )

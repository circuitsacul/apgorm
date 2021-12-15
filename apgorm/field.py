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

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from apgorm.describe import FieldDesc
from apgorm.exceptions import ReadOnlyField, UndefinedFieldValue
from apgorm.undefined import UNDEF

if TYPE_CHECKING:
    from apgorm.model import Model
    from apgorm.sql.sql import SQL, Block

    from .types.base_type import SqlType


_T = TypeVar("_T")
_F = TypeVar("_F", bound="SqlType")


class Field(Generic[_F, _T]):
    name: str  # populated by Database
    model: Type[Model]  # populated by Database

    def __init__(
        self,
        sql_type: _F,
        default: SQL[_T] | UNDEF = UNDEF.UNDEF,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        read_only: bool = False,
        references: Block | Field | None = None,
    ):
        self.sql_type = sql_type

        self.default = default

        self.not_null = not_null
        self.pk = pk
        self.unique = unique
        self.references = references

        self.read_only = read_only

        self.changed: bool = False
        self._value: _T | UNDEF = UNDEF.UNDEF

    def describe(self) -> FieldDesc:
        return FieldDesc(
            self.name,
            self.default,
            self.not_null,
            self.sql_type.describe(),
        )

    @property
    def full_name(self) -> str:
        return f"{self.model.tablename}.{self.name}"

    @property
    def value(self) -> _T:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self._value

    @value.setter
    def value(self, other: _T):
        if self.read_only:
            raise ReadOnlyField(self)
        self._value = other
        self.changed = True

    def _copy_kwargs(self) -> dict[str, Any]:
        return dict(
            sql_type=self.sql_type,
            default=self.default,
            not_null=self.not_null,
            pk=self.pk,
            unique=self.unique,
            read_only=self.read_only,
            references=self.references,
        )

    def copy(self) -> Field[_F, _T]:
        n = self.__class__(**self._copy_kwargs())
        n.name = self.name
        n.model = self.model
        return n

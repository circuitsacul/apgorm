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

from typing import TYPE_CHECKING, Any, Type, TypeVar

from apgorm.describe import ModelDesc
from apgorm.exceptions import ModelNotFound
from apgorm.field import Field
from apgorm.sql import (
    DeleteQueryBuilder,
    FetchQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
)
from apgorm.types.numeric import Serial
from apgorm.undefined import UNDEF

from .constraints import Constraint

if TYPE_CHECKING:
    from .database import Database


_T = TypeVar("_T", bound="Model")


class Model:
    tablename: str
    database: Database  # populated by Database

    uid = Serial().field(pk=True, read_only=True)

    def __init__(self, **values):
        if "uid" in values:
            self.uid._value = values["uid"]

        self.fields: dict[str, Field[Any, Any]] = {}
        self.constraints: dict[str, Constraint] = {}

        all_fields, all_constraints = self._special_attrs()
        for f in all_fields.values():
            f = f.copy()
            self.fields[f.name] = f
            setattr(self, f.name, f)

            value = values.get(f.name, UNDEF.UNDEF)
            if value is UNDEF.UNDEF:
                continue
            f._value = value

        for c in all_constraints.values():
            self.constraints[c.name] = c

    @classmethod
    def describe(cls) -> ModelDesc:
        fields, constraints = cls._special_attrs()
        return ModelDesc(
            cls.tablename,
            {f.name: f.describe() for f in fields.values()},
            {c.name: c.describe() for c in constraints.values()},
        )

    async def delete(self):
        await self.delete_query().where(uid=self.uid.v).execute()

    async def save(self):
        changed_fields = self._get_changed_fields()
        q = self.update_query().where(uid=self.uid.v)
        q.set(**{f.name: f.v for f in changed_fields})
        await q.execute()
        self._set_saved()

    async def create(self):
        q = self.insert_query()
        q.set(
            **{
                f.name: f.v
                for f in self.fields.values()
                if f._value is not UNDEF.UNDEF
            }
        )
        q.return_fields(
            *[f for f in self.fields.values() if f._value is UNDEF.UNDEF]
        )
        result = await q.execute()
        if len(q.fields_to_return) > 1:
            for f, v in zip(q.fields_to_return, result):
                f._value = v
        elif len(q.fields_to_return) == 1:
            q.fields_to_return[0]._value = result

    @classmethod
    async def fetch(cls: Type[_T], **values) -> _T:
        res = await cls.fetch_query().where(**values).fetchone()
        if res is None:
            raise ModelNotFound(cls, values)
        return res

    @classmethod
    def fetch_query(cls: Type[_T]) -> FetchQueryBuilder[_T]:
        return FetchQueryBuilder(model=cls)

    @classmethod
    def delete_query(cls: Type[_T]) -> DeleteQueryBuilder[_T]:
        return DeleteQueryBuilder(model=cls)

    @classmethod
    def update_query(cls: Type[_T]) -> UpdateQueryBuilder[_T]:
        return UpdateQueryBuilder(model=cls)

    @classmethod
    def insert_query(cls: Type[_T]) -> InsertQueryBuilder[_T]:
        return InsertQueryBuilder(model=cls)

    def _set_saved(self):
        for f in self.fields.values():
            f.changed = False

    def _get_changed_fields(self) -> list[Field]:
        return [f for f in self.fields.values() if f.changed]

    @classmethod
    def _special_attrs(cls) -> tuple[dict[str, Field], dict[str, Constraint]]:
        fields: dict[str, Field] = {}
        constraints: dict[str, Constraint] = {}

        for attr_name in dir(cls):
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            if isinstance(attr, Field):
                fields[attr_name] = attr

            elif isinstance(attr, Constraint):
                constraints[attr_name] = attr

        return fields, constraints

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

from __future__ import annotations, print_function

from typing import TYPE_CHECKING, Any, Type, TypeVar

from apgorm.exceptions import ModelNotFound, SpecifiedPrimaryKey
from apgorm.field import BaseField, ConverterField
from apgorm.migrations.describe import DescribeConstraint, DescribeTable
from apgorm.sql.query_builder import (
    DeleteQueryBuilder,
    FetchQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
)
from apgorm.undefined import UNDEF

from .constraints import Check, Constraint, ForeignKey, PrimaryKey, Unique

if TYPE_CHECKING:
    from .database import Database


_T = TypeVar("_T", bound="Model")


class Model:
    tablename: str  # populated by Database
    database: Database  # populated by Database

    primary_key: tuple[BaseField, ...]

    def __init__(self, **values):
        self.fields: dict[str, BaseField] = {}
        self.constraints: dict[str, Constraint] = {}

        all_fields, all_constraints = self._special_attrs()
        for f in all_fields.values():
            f = f.copy()
            self.fields[f.name] = f
            setattr(self, f.name, f)

            value = values.get(f.name, UNDEF.UNDEF)
            if value is UNDEF.UNDEF:
                continue
            if isinstance(f, ConverterField):
                f._value = f.converter.to_stored(value)
            else:
                f._value = value

        # carry the copies of the fields over to primary_key so that
        # Model.field is Model.primary_key[index of that field]
        self.primary_key = tuple(
            [self.fields[f.name] for f in self.primary_key]
        )

        for c in all_constraints.values():
            self.constraints[c.name] = c

    @classmethod
    def _primary_key(cls) -> PrimaryKey:
        pk = PrimaryKey(cls.primary_key)
        pk.name = (
            f"{cls.tablename}_"
            + "{}".format("_".join([f.name for f in cls.primary_key]))
            + "_primary_key"
        )
        return pk

    @classmethod
    def describe(cls) -> DescribeTable:
        fields, constraints = cls._special_attrs()
        unique: list[DescribeConstraint] = []
        check: list[DescribeConstraint] = []
        fk: list[DescribeConstraint] = []
        for c in constraints.values():
            if isinstance(c, Check):
                check.append(c.describe())
            elif isinstance(c, ForeignKey):
                fk.append(c.describe())
            elif isinstance(c, Unique):
                unique.append(c.describe())

        return DescribeTable(
            cls.tablename,
            [f.describe() for f in fields.values()],
            fk,
            cls._primary_key().describe(),
            unique,
            check,
        )

    def _pk_field_values(self) -> dict[str, Any]:
        return {f.name: f.v for f in self.primary_key}

    async def delete(self):
        await self.delete_query().where(**self._pk_field_values()).execute()

    async def save(self):
        changed_fields = self._get_changed_fields()
        if len(changed_fields) == 0:
            return
        q = self.update_query().where(**self._pk_field_values())
        q.set(**{f.name: f._value for f in changed_fields})
        await q.execute()
        self._set_saved()

    async def create(self):
        q = self.insert_query()
        q.set(
            **{
                f.name: f._value
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

    def _get_changed_fields(self) -> list[BaseField]:
        return [f for f in self.fields.values() if f.changed]

    @classmethod
    def _special_attrs(
        cls,
    ) -> tuple[dict[str, BaseField], dict[str, Constraint]]:
        fields: dict[str, BaseField] = {}
        constraints: dict[str, Constraint] = {}

        for attr_name in dir(cls):
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            if isinstance(attr, BaseField):
                fields[attr_name] = attr

            elif isinstance(attr, Constraint):
                if isinstance(attr, PrimaryKey):
                    raise SpecifiedPrimaryKey(
                        cls.__name__,
                        [
                            f.name
                            if isinstance(f, BaseField)
                            else f.render_no_params()
                            for f in attr.fields
                        ],
                    )
                constraints[attr_name] = attr

        return fields, constraints

    # magic methods
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            + " ".join(
                [
                    f"{f.name}:{f.v!r}"
                    for f in self.fields.values()
                    if f.use_repr and f._value is not UNDEF.UNDEF
                ]
            )
            + ">"
        )

    def _eq_fields(self) -> dict[str, Any]:
        return {f.name: f.v for f in self.primary_key}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Unsupported type {type(other)}.")

        return self._eq_fields() == other._eq_fields()

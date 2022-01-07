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

from typing import TYPE_CHECKING, Any, Type, TypeVar, cast

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

from .constraints import (
    Check,
    Constraint,
    Exclude,
    ForeignKey,
    PrimaryKey,
    Unique,
)

if TYPE_CHECKING:
    from .connection import Connection
    from .database import Database


_T = TypeVar("_T", bound="Model")


class Model:
    """Base class for all models. To create a new model, subclass this class
    and add it to your database like this:

    ```
    class User(Model):
        username = VarChar(32).field()
        ...

        primary_key = (username,)

    ...

    class MyDatabase(Database):
        users = User
        ...
    ```
    """

    _all_fields: dict[str, BaseField]
    _all_constraints: dict[str, Constraint]

    _tablename: str  # populated by Database
    """The name of the table, populated by Database."""
    _database: Database  # populated by Database
    """The database instance, populated by Database."""

    primary_key: tuple[BaseField, ...]
    """The primary key for the model. All models MUST have a primary key."""

    def __init__(self, **values):
        """Create an instance of the model. There are two reasons you might do this:
         1. You used `Database.fetch...` directly instead of
         `Model.fetch`, and you want to convert the result to a model.
         2. You want to create a new model (`Model(**values).create()`).

        If you wish to fetch an existing model, please use `Model.fetch` or
        `Model.fetch_query`.
        """

        self._all_fields: dict[str, BaseField] = {}
        self._all_constraints: dict[str, Constraint] = {}

        all_fields, all_constraints = self._special_attrs()
        for f in all_fields.values():
            f = f.copy()
            self._all_fields[f.name] = f
            setattr(self, f.name, f)

            value = values.get(f.name, UNDEF.UNDEF)
            if value is UNDEF.UNDEF:
                d = f._get_default()
                if d is not UNDEF.UNDEF:
                    value = d
                else:
                    continue
            if isinstance(f, ConverterField):
                f._value = f.converter.to_stored(value)
            else:
                f._value = value

        # carry the copies of the fields over to primary_key so that
        # Model.field is Model.primary_key[index of that field]
        self.primary_key = tuple(
            [self._all_fields[f.name] for f in self.primary_key]
        )

        for c in all_constraints.values():
            self._all_constraints[c.name] = c

    @classmethod
    def _primary_key(cls) -> PrimaryKey:
        pk = PrimaryKey(*cls.primary_key)
        pk.name = (
            f"_{cls._tablename}_"
            + "{}".format("_".join([f.name for f in cls.primary_key]))
            + "_primary_key"
        )
        return pk

    @classmethod
    def _describe(cls) -> DescribeTable:
        fields, constraints = cls._special_attrs()
        unique: list[DescribeConstraint] = []
        check: list[DescribeConstraint] = []
        fk: list[DescribeConstraint] = []
        exclude: list[DescribeConstraint] = []
        for c in constraints.values():
            if isinstance(c, Check):
                check.append(c._describe())
            elif isinstance(c, ForeignKey):
                fk.append(c._describe())
            elif isinstance(c, Unique):
                unique.append(c._describe())
            elif isinstance(c, Exclude):
                exclude.append(c._describe())

        return DescribeTable(
            name=cls._tablename,
            fields=[f._describe() for f in fields.values()],
            fk_constraints=fk,
            pk_constraint=cls._primary_key()._describe(),
            unique_constraints=unique,
            check_constraints=check,
            exclude_constraints=exclude,
        )

    def _pk_fields(self) -> dict[str, Any]:
        return {f.name: f.v for f in self.primary_key}

    async def delete(self, con: Connection | None = None):
        """Delete the model."""

        await self.delete_query(con=con).where(**self._pk_fields()).execute()

    async def save(self, con: Connection | None = None):
        """Save any changed fields of the model."""

        changed_fields = self._get_changed_fields()
        if len(changed_fields) == 0:
            return
        q = self.update_query(con=con).where(**self._pk_fields())
        q.set(**{f.name: f._value for f in changed_fields})
        await q.execute()
        self._set_saved()

    async def create(self, con: Connection | None = None):
        """Inser the model into the database."""

        q = self.insert_query(con=con)
        q.set(
            **{
                f.name: f._value
                for f in self._all_fields.values()
                if f._value is not UNDEF.UNDEF
            }
        )
        q.return_fields(
            *[f for f in self._all_fields.values() if f._value is UNDEF.UNDEF]
        )
        result = await q.execute()

        fields_to_return = cast("list[BaseField]", q.fields_to_return)
        assert all([isinstance(f, BaseField) for f in fields_to_return])

        if len(fields_to_return) > 1:
            for f, v in zip(fields_to_return, result):
                f._value = v
        elif len(fields_to_return) == 1:
            fields_to_return[0]._value = result

    @classmethod
    async def fetch(
        cls: Type[_T],
        con: Connection | None = None,
        /,
        **values,
    ) -> _T:
        """Fetch an exiting model from the database.

        Example:
        ```
        User.fetch(username="Circuit")
        ```

        Raises:
            ModelNotFound: No model for the given parameters were found.

        Returns:
            Model: The model.
        """

        res = await cls.fetch_query(con=con).where(**values).fetchone()
        if res is None:
            raise ModelNotFound(cls, values)
        return res

    @classmethod
    def fetch_query(
        cls: Type[_T], con: Connection | None = None
    ) -> FetchQueryBuilder[_T]:
        """Returns a FetchQueryBuilder."""

        return FetchQueryBuilder(model=cls, con=con)

    @classmethod
    def delete_query(
        cls: Type[_T], con: Connection | None = None
    ) -> DeleteQueryBuilder[_T]:
        """Returns a DeleteQueryBuilder."""

        return DeleteQueryBuilder(model=cls, con=con)

    @classmethod
    def update_query(
        cls: Type[_T], con: Connection | None = None
    ) -> UpdateQueryBuilder[_T]:
        """Returns an UpdateQueryBuilder."""

        return UpdateQueryBuilder(model=cls, con=con)

    @classmethod
    def insert_query(
        cls: Type[_T], con: Connection | None = None
    ) -> InsertQueryBuilder[_T]:
        """Returns an InsertQueryBuilder."""

        return InsertQueryBuilder(model=cls, con=con)

    def _set_saved(self):
        for f in self._all_fields.values():
            f.changed = False

    def _get_changed_fields(self) -> list[BaseField]:
        return [f for f in self._all_fields.values() if f.changed]

    @classmethod
    def _special_attrs(
        cls,
    ) -> tuple[dict[str, BaseField], dict[str, Constraint]]:
        if hasattr(cls, "_all_fields") and hasattr(cls, "_all_constraints"):
            return cls._all_fields, cls._all_constraints

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

        cls._all_fields = fields
        cls._all_constraints = constraints

        return fields, constraints

    # magic methods
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            + " ".join(
                [
                    f"{f.name}:{f.v!r}"
                    for f in self._all_fields.values()
                    if f.use_repr and f._value is not UNDEF.UNDEF
                ]
            )
            + ">"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Unsupported type {type(other)}.")

        return self._pk_fields() == other._pk_fields()

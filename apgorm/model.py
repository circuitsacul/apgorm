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

from .constraints.check import Check
from .constraints.constraint import Constraint
from .constraints.exclude import Exclude
from .constraints.foreign_key import ForeignKey
from .constraints.primary_key import PrimaryKey
from .constraints.unique import Unique
from .exceptions import ModelNotFound, SpecifiedPrimaryKey
from .field import BaseField, ConverterField
from .manytomany import ManyToMany
from .migrations.describe import DescribeConstraint, DescribeTable
from .sql.query_builder import (
    DeleteQueryBuilder,
    FetchQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
)
from .undefined import UNDEF

if TYPE_CHECKING:  # pragma: no cover
    from .connection import Connection
    from .database import Database


_SELF = TypeVar("_SELF", bound="Model")


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

    Use Model() to create an instance of the model. There are two reasons you
    might do this:
        1. You used `Database.fetch...` directly instead of `Model.fetch`, and
        you want to convert the result to a model.
        2. You want to create a new model (`Model(**values).create()`).

    If you wish to fetch an existing model, please use `Model.fetch` or
    `Model.fetch_query`.
    """

    all_fields: dict[str, BaseField]
    all_constraints: dict[str, Constraint]
    _all_mtm: dict[str, ManyToMany]

    tablename: str  # populated by Database
    """The name of the table, populated by Database."""
    database: Database  # populated by Database
    """The database instance, populated by Database."""

    primary_key: tuple[BaseField, ...]
    """The primary key for the model. All models MUST have a primary key."""

    def __init__(self, override_validator: bool = False, /, **values) -> None:
        copied_fields: dict[str, BaseField] = {}

        for f in self.all_fields.values():
            f = f.copy()
            copied_fields[f.name] = f
            setattr(self, f.name, f)

            convert: bool = True
            value = values.get(f.name, UNDEF.UNDEF)
            if value is UNDEF.UNDEF:
                d = f._get_default()
                convert = False
                if d is not UNDEF.UNDEF:
                    value = d
                else:
                    continue  # pragma: no cover  # (pytest bug)
            if isinstance(f, ConverterField) and convert:
                if not override_validator:
                    f._validate(value)
                f._value = f.converter.to_stored(value)
            else:
                if not override_validator:
                    if isinstance(f, ConverterField):
                        f._validate(f.converter.from_stored(value))
                    else:
                        f._validate(value)
                f._value = value

        # carry the copies of the fields over to primary_key so that
        # Model.field is Model.primary_key[index of that field]
        self.primary_key = tuple(
            [copied_fields[f.name] for f in self.primary_key]
        )

        self.all_fields = copied_fields

        for name, mtm in self._all_mtm.items():
            mtm = mtm._generate_mtm(self)
            setattr(self, name, mtm)

    async def delete(self: _SELF, con: Connection | None = None) -> _SELF:
        """Delete the model. Does not update the values of this model,
        but the returned model will have updated values.

        Returns:
            Model: The deleted model (with updated values).
        """

        deleted = (
            await self.delete_query(con=con)
            .where(**(f := self._pk_fields()))
            .execute()
        )
        if len(deleted) == 0:
            raise ModelNotFound(self.__class__, f)
        return deleted[0]

    async def save(self, con: Connection | None = None) -> None:
        """Save any changed fields of the model. Updates the values
        of this model."""

        changed_fields = self._get_changed_fields()
        if len(changed_fields) == 0:
            return
        q = self.update_query(con=con).where(**self._pk_fields())
        q.set(**{f.name: f._value for f in changed_fields})
        result = await q.execute()
        self._update_from_model(result[0])
        self._set_saved()

    async def create(self: _SELF, con: Connection | None = None) -> _SELF:
        """Insert the model into the database. Updates the values on this
        model.

        Returns:
            Model: The model that was inserted. Useful if you want to write
            `model = await Model(...).create()`
        """

        q = self.insert_query(con=con)
        q.set(
            **{
                f.name: f._value
                for f in self.all_fields.values()
                if f._value is not UNDEF.UNDEF
            }
        )
        self._update_from_model(await q.execute())

        return self

    async def refetch(self: _SELF, con: Connection | None = None) -> None:
        """Updates the model instance by fetching changed values from the
        database."""

        res = await self.fetch(con, **self._pk_fields())
        self._update_from_model(res)

    @classmethod
    async def exists(
        cls: Type[_SELF], con: Connection | None = None, /, **values
    ) -> _SELF | None:
        """Check if a model with the given values exists.

        ```
        assert (await User.exists(nickname=None)) is not None
        ```

        This method can also be used to get the `model or None`, whereas
        `.fetch()` will raise an exception if the model does not exist.

        Returns:
            Model | None: The model if it existed, otherwise None.
        """

        try:
            return await cls.fetch(con, **values)
        except ModelNotFound:
            return None

    @classmethod
    async def fetch(
        cls: Type[_SELF],
        con: Connection | None = None,
        /,
        **values,
    ) -> _SELF:
        """Fetch an exiting model from the database.

        Example:
        ```
        user = await User.fetch(username="Circuit")
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
        cls: Type[_SELF], con: Connection | None = None
    ) -> FetchQueryBuilder[_SELF]:
        """Returns a FetchQueryBuilder."""

        return FetchQueryBuilder(model=cls, con=con)

    @classmethod
    def delete_query(
        cls: Type[_SELF], con: Connection | None = None
    ) -> DeleteQueryBuilder[_SELF]:
        """Returns a DeleteQueryBuilder."""

        return DeleteQueryBuilder(model=cls, con=con)

    @classmethod
    def update_query(
        cls: Type[_SELF], con: Connection | None = None
    ) -> UpdateQueryBuilder[_SELF]:
        """Returns an UpdateQueryBuilder."""

        return UpdateQueryBuilder(model=cls, con=con)

    @classmethod
    def insert_query(
        cls: Type[_SELF], con: Connection | None = None
    ) -> InsertQueryBuilder[_SELF]:
        """Returns an InsertQueryBuilder."""

        return InsertQueryBuilder(model=cls, con=con)

    def _update_from_model(self: _SELF, updated: _SELF) -> None:
        for f in updated.all_fields.values():
            self.all_fields[f.name]._value = f._value

    @classmethod
    def _primary_key(cls) -> PrimaryKey:
        pk = PrimaryKey(*cls.primary_key)
        pk.name = (
            f"_{cls.tablename}_"
            + "{}".format("_".join([f.name for f in cls.primary_key]))
            + "_primary_key"
        )
        return pk

    @classmethod
    def _describe(cls) -> DescribeTable:
        unique: list[DescribeConstraint] = []
        check: list[DescribeConstraint] = []
        fk: list[DescribeConstraint] = []
        exclude: list[DescribeConstraint] = []
        for c in cls.all_constraints.values():
            if isinstance(c, Check):
                check.append(c._describe())
            elif isinstance(c, ForeignKey):
                fk.append(c._describe())
            elif isinstance(c, Unique):
                unique.append(c._describe())
            elif isinstance(c, Exclude):
                exclude.append(c._describe())

        return DescribeTable(
            name=cls.tablename,
            fields=[f._describe() for f in cls.all_fields.values()],
            fk_constraints=fk,
            pk_constraint=cls._primary_key()._describe(),
            unique_constraints=unique,
            check_constraints=check,
            exclude_constraints=exclude,
        )

    @classmethod
    def _special_attrs(
        cls,
    ) -> tuple[dict[str, BaseField], dict[str, Constraint]]:
        fields: dict[str, BaseField] = {}
        constraints: dict[str, Constraint] = {}
        mtm: dict[str, ManyToMany] = {}

        for attr_name in dir(cls):
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:  # pragma: no cover
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

            elif isinstance(attr, ManyToMany):
                mtm[attr_name] = attr

        cls.all_fields = fields
        cls.all_constraints = constraints
        cls._all_mtm = mtm

        return fields, constraints

    def _pk_fields(self) -> dict[str, Any]:
        return {f.name: f.v for f in self.primary_key}

    def _set_saved(self) -> None:
        for f in self.all_fields.values():
            f.changed = False

    def _get_changed_fields(self) -> list[BaseField]:
        return [f for f in self.all_fields.values() if f.changed]

    # magic methods
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} "
            + " ".join(
                [
                    f"{f.name}:{f.v!r}"
                    for f in self.all_fields.values()
                    if f.use_repr and f._value is not UNDEF.UNDEF
                ]
            )
            + ">"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            raise TypeError(f"Unsupported type {type(other)}.")

        return self._pk_fields() == other._pk_fields()

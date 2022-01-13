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

from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Callable,
    Generic,
    Type,
    TypeVar,
)

from apgorm.undefined import UNDEF
from apgorm.utils.lazy_list import LazyList

from .generators.query import delete, insert, select, update
from .sql import SQL, Block, and_, r, sql, wrap

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.connection import Connection
    from apgorm.model import Model
    from apgorm.types.boolean import Bool

_T = TypeVar("_T", bound="Model")


def _dict_model_converter(model: Type[_T]) -> Callable[[dict[str, Any]], _T]:
    def converter(values: dict[str, Any]) -> _T:
        return model(True, **values)

    return converter


class BaseQueryBuilder(Generic[_T]):
    """Base class for query builders."""

    def __init__(self, model: Type[_T], con: Connection | None = None) -> None:
        self.model = model
        self.con = con or model.database

    def _get_block(self) -> Block:
        """Convert the data in the query builder to a Block."""

        raise NotImplementedError  # pragma: no cover


_S = TypeVar("_S", bound="FilterQueryBuilder")


class FilterQueryBuilder(BaseQueryBuilder[_T]):
    """Base class for query builders that have "where logic"."""

    def __init__(self, model: Type[_T], con: Connection | None = None) -> None:
        super().__init__(model, con)

        self._filters: list[Block[Bool]] = []

    def where(self: _S, *filters: Block[Bool], **values: SQL) -> _S:
        """Extend the current where logic.

        Example:
        ```
        builder.where(User.nickname.neq("Nickname"), status=4)
        # nickname != "Nickname", status == 4
        ```

        Returns:
            FilterQueryBuilder: Returns the query builder to allow for
            chaining.
        """

        # NOTE: Although **values might look like an SQL-injection
        # vulnerability, it's really not. Since the keys for **values
        # can only contain A-Za-z_ characters, there's no possibly way
        # to perform sql injection, even if the keys are user input.
        self._filters.extend(filters)
        for k, v in values.items():
            self._filters.append(r(k).eq(v))

        return self

    def _where_logic(self) -> Block[Bool] | None:
        if len(self._filters) == 0:
            return None
        return and_(*self._filters)


class FetchQueryBuilder(FilterQueryBuilder[_T]):
    """Query builder for fetching models."""

    def __init__(self, model: Type[_T], con: Connection | None = None) -> None:
        super().__init__(model, con)

        self._order_by_logic: SQL | UNDEF = UNDEF.UNDEF
        self._reverse: bool = False

    def order_by(
        self,
        logic: SQL,
        reverse: bool = False,
    ) -> FetchQueryBuilder[_T]:
        """Specify the order logic of the query.

        Args:
            field (Block | BaseField): The field or raw field name to order by.
            reverse (bool, optional): If set, will return results decending
            instead of ascending.

        Returns:
            FetchQueryBuilder: Returns the query builder to allow for chaining.
        """

        self._order_by_logic = logic
        self._reverse = reverse
        return self

    def exists(self) -> Block[Bool]:
        """Returns this query wrapped in EXISTS (). Useful for subqueries:

        ```
        user = await User.fetch(name="Circuit")
        games = await Game.fetch_query().where(
            Player.fetch_query().where(
                gameid=Game.id_, username=user.name.v
            ).exists()
        ).fetchmany()
        ```

        Returns:
            Block[Bool]: The subquery.
        """

        return sql(r("EXISTS"), wrap(self._get_block()))

    async def fetchmany(self, limit: int | None = None) -> LazyList[dict, _T]:
        """Execute the query and return a list of models.

        Args:
            limit (int, optional): The maximum number of models to return.
            Defaults to None.

        Raises:
            TypeError: You specified a limit that wasn't an integer (must be a
            python int).

        Returns:
            LazyList[dict, Model]: The list of models matching the query.
        """

        if limit is not None and not isinstance(limit, int):
            # NOTE: although limit as a string would work, there is a good
            # chance that it's a string because it was user input, meaning
            # that allowing limit to be a string would create an SQL-injection
            # vulnerability.
            raise TypeError("Limit can only be an int.")
        res = await self.con.fetchmany(*self._get_block(limit).render())
        return LazyList(res, _dict_model_converter(self.model))

    async def fetchone(self) -> _T | None:
        """Fetch the first model found.

        Returns:
            Model | None: Returns the model, or None if none were found.
        """

        res = await self.con.fetchrow(*self._get_block().render())
        if res is None:
            return None
        return self.model(True, **res)

    async def cursor(self) -> AsyncGenerator[_T, None]:
        """Return an iterator of the resulting models.

        Yields:
            Model: The (next) model from the iterator.
        """

        con = self.con if isinstance(self.con, Connection) else None
        async with self.model.database.cursor(
            *self._get_block().render(), con=con
        ) as cursor:
            async for res in cursor:
                yield self.model(True, **res)

    def _get_block(self, limit: int | None = None) -> Block:
        return select(
            from_=self.model,
            where=self._where_logic(),
            order_by=self._order_by_logic,
            reverse=self._reverse,
            limit=limit,
        )


class DeleteQueryBuilder(FilterQueryBuilder[_T]):
    """Query builder for deleting models."""

    async def execute(self) -> LazyList[dict, _T]:
        """Execute the deletion query.

        Returns:
            LazyList[dict, Model]: List of models deleted.
        """

        res = await self.con.fetchmany(*self._get_block().render())
        return LazyList(res, _dict_model_converter(self.model))

    def _get_block(self) -> Block:
        return delete(
            self.model,
            self._where_logic(),
            list(self.model.all_fields.values()),
        )


class UpdateQueryBuilder(FilterQueryBuilder[_T]):
    """Query builder for updating models."""

    def __init__(self, model: Type[_T], con: Connection | None = None) -> None:
        super().__init__(model, con)

        self._set_values: dict[Block, SQL] = {}

    def set(self, **values: SQL) -> UpdateQueryBuilder[_T]:
        """Specify changes in the model.

        Example:
        ```
        builder.set(username="New Name")
        ```

        Returns:
            UpdateQueryBuilder: Returns the query builder to allow for
            chaining.
        """

        self._set_values.update({r(k): v for k, v in values.items()})
        return self

    async def execute(self) -> LazyList[dict, _T]:
        """Execute the query.

        Returns:
            LazyList[dict, Model]: List of updated models.
        """

        res = await self.con.fetchmany(*self._get_block().render())
        return LazyList(res, _dict_model_converter(self.model))

    def _get_block(self) -> Block:
        return update(
            self.model,
            {k: v for k, v in self._set_values.items()},
            where=self._where_logic(),
            return_fields=list(self.model.all_fields.values()),
        )


class InsertQueryBuilder(BaseQueryBuilder[_T]):
    """Query builder for creating a model."""

    def __init__(self, model: Type[_T], con: Connection | None = None) -> None:
        super().__init__(model, con)

        self._set_values: dict[Block, SQL] = {}

    def set(self, **values: SQL) -> InsertQueryBuilder[_T]:
        """Specify values to be set in the database.

        ```
        await User.insert_query().set(username="Circuit").execute()
        ```

        Returns:
            InsertQueryBuilder: Returns the query builder to allow for
            chaining.
        """

        self._set_values.update({r(k): v for k, v in values.items()})
        return self

    async def execute(self) -> _T:
        """Execute the query.

        Returns:
            Model: The model that was inserted.
        """

        return self.model(
            True, **await self.con.fetchrow(*self._get_block().render())
        )

    def _get_block(self) -> Block:
        value_names = [n for n in self._set_values.keys()]
        value_values = [v for v in self._set_values.values()]

        return insert(
            self.model,
            value_names,
            value_values,
            return_fields=list(self.model.all_fields.values()),
        )

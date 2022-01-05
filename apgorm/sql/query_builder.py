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

from typing import TYPE_CHECKING, Any, AsyncGenerator, Generic, Type, TypeVar

from apgorm.field import BaseField

from .generators.query import delete, insert, select, update
from .sql import SQL, Block, r

if TYPE_CHECKING:
    from apgorm.connection import Connection
    from apgorm.model import Model
    from apgorm.types.boolean import Bool

_T = TypeVar("_T", bound="Model")


class Query(Generic[_T]):
    def __init__(self, model: Type[_T], con: Connection | None = None):
        self.model = model
        self.con = con or model._database


_S = TypeVar("_S", bound="FilterQueryBuilder")


class FilterQueryBuilder(Query[_T]):
    def __init__(self, model: Type[_T], con: Connection | None = None):
        super().__init__(model, con)

        self.filters: list[Block[Bool]] = []

    def where_logic(self) -> Block[Bool] | None:
        if len(self.filters) == 0:
            return None
        return self.filters.pop(0).and_(*self.filters)

    def where(self: _S, *filters: Block[Bool], **values: SQL) -> _S:
        # NOTE: Although **values might look like an SQL-injection
        # vulnerability, it's really not. Since the keys for **values
        # can only contain A-Za-z_ characters, there's no possibly way
        # to perform sql injection, even if the keys are user input.
        self.filters.extend(filters)
        for k, v in values.items():
            self.filters.append(r(k).eq(v))

        return self


class FetchQueryBuilder(FilterQueryBuilder[_T]):
    def __init__(self, model: Type[_T], con: Connection | None = None):
        super().__init__(model, con)

        self.order_by_field: BaseField | Block | None = None
        self.ascending: bool = True

    def order_by(
        self,
        field: Block | BaseField,
        ascending: bool = True,
    ) -> FetchQueryBuilder[_T]:
        self.order_by_field = field
        self.ascending = ascending
        return self

    def _fetch_query(self, limit: int | None = None) -> tuple[str, list[Any]]:
        return select(
            from_=self.model,
            where=self.where_logic(),
            order_by=self.order_by_field,
            ascending=self.ascending,
            limit=limit,
        ).render()

    async def fetchmany(self, limit: int | None = None) -> list[_T]:
        if not isinstance(limit, int):
            # NOTE: although limit as a string would work, there is a good
            # chance that it's a string because it was user input, meaning
            # that allowing limit to be a string would create an SQL-injection
            # vulnerability.
            raise TypeError("Limit can only be an int.")
        query, params = self._fetch_query(limit=limit)
        res = await self.con.fetchmany(query, params)
        return [self.model(**r) for r in res]

    async def fetchone(self) -> _T | None:
        query, params = self._fetch_query()
        res = await self.con.fetchrow(query, params)
        if res is None:
            return None
        return self.model(**res)

    async def cursor(self) -> AsyncGenerator[_T, None]:
        query, params = self._fetch_query()
        con = self.con if isinstance(self.con, Connection) else None
        async with self.model._database.cursor(
            query, params, con=con
        ) as cursor:
            async for res in cursor:
                yield self.model(**res)


class DeleteQueryBuilder(FilterQueryBuilder[_T]):
    async def execute(self):
        query, params = delete(self.model, self.where_logic()).render()
        await self.model._database.execute(query, params)


class UpdateQueryBuilder(FilterQueryBuilder[_T]):
    def __init__(self, model: Type[_T], con: Connection | None = None):
        super().__init__(model, con)

        self.set_values: dict[Block, SQL] = {}

    def set(self, **values: SQL) -> UpdateQueryBuilder[_T]:
        self.set_values.update({r(k): v for k, v in values.items()})
        return self

    async def execute(self):
        query, params = update(
            self.model,
            {k: v for k, v in self.set_values.items()},
            where=self.where_logic(),
        ).render()
        await self.con.execute(query, params)


class InsertQueryBuilder(Query[_T]):
    def __init__(self, model: Type[_T], con: Connection | None = None):
        super().__init__(model, con)

        self.set_values: dict[Block, SQL] = {}
        self.fields_to_return: list[Block | BaseField] = []

    def set(self, **values: SQL) -> InsertQueryBuilder[_T]:
        self.set_values.update({r(k): v for k, v in values.items()})
        return self

    def return_fields(
        self, *fields: Block | BaseField
    ) -> InsertQueryBuilder[_T]:
        self.fields_to_return.extend(fields)
        return self

    async def execute(self) -> Any:
        value_names = [n for n in self.set_values.keys()]
        value_values = [v for v in self.set_values.values()]

        query, params = insert(
            self.model,
            value_names,
            value_values,
            return_fields=self.fields_to_return or None,
        ).render()
        return await self.con.fetchval(query, params)

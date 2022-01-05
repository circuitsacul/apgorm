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
    from apgorm.model import Model
    from apgorm.types.boolean import Bool

_T = TypeVar("_T", bound="Model")


class Query(Generic[_T]):
    def __init__(self, model: Type[_T]):
        self.model = model


_S = TypeVar("_S", bound="FilterQueryBuilder")


class FilterQueryBuilder(Query[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

        self.filters: list[Block[Bool]] = []

    def where_logic(self) -> Block[Bool] | None:
        if len(self.filters) == 0:
            return None
        return self.filters.pop().and_(*self.filters)

    def where(self: _S, *filters: Block[Bool], **values: SQL) -> _S:
        self.filters.extend(filters)
        for k, v in values.items():
            key = r(f"{self.model.tablename}.{k}")
            self.filters.append(key.eq(v))

        return self


class FetchQueryBuilder(FilterQueryBuilder[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

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

    def _fetch_query(self) -> tuple[str, list[Any]]:
        return select(
            from_=self.model,
            where=self.where_logic(),
            order_by=self.order_by_field,
            ascending=self.ascending,
        ).render()

    async def fetchmany(self) -> list[_T]:
        query, params = self._fetch_query()
        res = await self.model.database.fetchmany(query, params)
        return [self.model(**r) for r in res]

    async def fetchone(self) -> _T | None:
        query, params = self._fetch_query()
        res = await self.model.database.fetchrow(query, params)
        if res is None:
            return None
        return self.model(**res)

    async def cursor(self) -> AsyncGenerator[_T, None]:
        query, params = self._fetch_query()
        async with self.model.database.cursor(query, params) as cursor:
            async for res in cursor:
                yield self.model(**res)


class DeleteQueryBuilder(FilterQueryBuilder[_T]):
    async def execute(self):
        query, params = delete(self.model, self.where_logic()).render()
        await self.model.database.execute(query, params)


class UpdateQueryBuilder(FilterQueryBuilder[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

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
        await self.model.database.execute(query, params)


class InsertQueryBuilder(Query[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

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
        return await self.model.database.fetchval(query, params)

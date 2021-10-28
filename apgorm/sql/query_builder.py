from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from apgorm.field import Field

from .generators.comp import and_, eq
from .generators.helpers import r
from .generators.query import delete, insert, select, update
from .render import render
from .sql import SQL, Sql

if TYPE_CHECKING:
    from apgorm.model import Model

_T = TypeVar("_T", bound="Model")


class Query(Generic[_T]):
    def __init__(self, model: Type[_T]):
        self.model = model


class FilterQuery(Query[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

        self.filters: list[Sql[bool]] = []

    def where_logic(self) -> Sql[bool] | None:
        if len(self.filters) == 0:
            return None
        return and_(*self.filters)

    def where(self, *filters: Sql[bool], **values: SQL):
        self.filters.extend(filters)
        for k, v in values.items():
            if isinstance(v, Field):
                v = r(v.full_name)
            key = r(f"{self.model.tablename}.{k}")
            self.filters.append(eq(key, v))

        return self


class FetchQuery(FilterQuery[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

        self.order_by_field: Field | Sql | None = None
        self.ascending: bool = True

    def order_by(
        self,
        field: Sql | Field,
        ascending: bool = True,
    ) -> FetchQuery[_T]:
        self.order_by_field = field
        self.ascending = ascending
        return self

    def _fetch_query(self) -> tuple[str, list[Any]]:
        return render(
            select(
                from_=self.model,
                where=self.where_logic(),
                order_by=self.order_by_field,
                ascending=self.ascending,
            )
        )

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


class DeleteQuery(FilterQuery[_T]):
    async def execute(self):
        query, params = render(delete(self.model, self.where_logic()))
        await self.model.database.execute(query, params)


class UpdateQuery(FilterQuery[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

        self.set_values: dict[Sql, SQL] = {}

    def set(self, **values: SQL) -> UpdateQuery[_T]:
        self.set_values.update({r(k): v for k, v in values.items()})
        return self

    async def execute(self):
        query, params = render(
            update(
                self.model,
                {k: v for k, v in self.set_values.items()},
                where=self.where_logic(),
            )
        )
        await self.model.database.execute(query, params)


class InsertQuery(Query[_T]):
    def __init__(self, model: Type[_T]):
        super().__init__(model)

        self.set_values: dict[Sql, SQL] = {}

    def set(self, **values: SQL) -> InsertQuery[_T]:
        self.set_values.update({r(k): v for k, v in values.items()})
        return self

    async def execute(self) -> Any:
        value_names = [n for n in self.set_values.keys()]
        value_values = [v for v in self.set_values.values()]

        query, params = render(
            insert(
                self.model,
                value_names,
                value_values,
                return_fields=self.model.uid,
            )
        )
        uid = await self.model.database.fetchval(query, params)
        return uid

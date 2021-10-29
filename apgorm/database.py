from __future__ import annotations

from typing import Any, Type

import asyncpg

from .model import Model


class Database:
    def __init__(self):
        self.models: list[Type[Model]] = []

        for attr_name in dir(self):
            try:
                attr = getattr(self, attr_name)
            except AttributeError:
                continue

            if not isinstance(attr, type):
                continue
            if not issubclass(attr, Model):
                continue

            attr.database = self
            self.models.append(attr)

            fields, constraints = attr._special_attrs()
            for name, field in fields.items():
                field.model = attr
                field.name = name

            for name, constraint in constraints.items():
                constraint.name = name

        self.pool: asyncpg.Pool | None = None

    async def connect(self, **connect_kwargs):
        self.pool = await asyncpg.create_pool(**connect_kwargs)

    async def execute(self, query: str, args: list[Any]):
        print(query, args)
        assert self.pool is not None
        await self.pool.execute(query, *args)

    async def fetchrow(
        self, query: str, args: list[Any]
    ) -> dict[str, Any] | None:
        print(query, args)
        assert self.pool is not None
        res = await self.pool.fetchrow(query, *args)
        if res is not None:
            res = dict(res)
        assert res is None or isinstance(res, dict)
        return res

    async def fetchmany(
        self, query: str, args: list[Any]
    ) -> list[dict[str, Any]]:
        print(query, args)
        assert self.pool is not None
        res = await self.pool.fetch(query, *args)
        return [dict(r) for r in res]

    async def fetchval(self, query: str, args: list[Any]) -> Any:
        print(query, args)
        assert self.pool is not None
        return await self.pool.fetchval(query, *args)

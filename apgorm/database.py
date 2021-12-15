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

import asyncio
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

    async def cleanup(self, timeout: float = 30):
        if self.pool is not None:
            await asyncio.wait_for(self.pool.close(), timeout=timeout)

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

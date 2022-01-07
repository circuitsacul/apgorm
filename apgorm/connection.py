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

from typing import Any, Coroutine

import asyncpg
from asyncpg.cursor import CursorFactory
from asyncpg.transaction import Transaction


class PoolAcquireContext:
    def __init__(self, pac: asyncpg.pool.PoolAcquireContext):
        self.pac = pac

    async def __aenter__(self) -> Connection:
        return Connection(await self.pac.__aenter__())

    async def __aexit__(self, *exc) -> None:
        await self.pac.__aexit__(*exc)

    async def __await__(self) -> Connection:
        return Connection(await self.pac.__await__())


class Pool:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    def acquire(self) -> PoolAcquireContext:
        return PoolAcquireContext(self.pool.acquire())

    def close(self) -> Coroutine[Any, Any, None]:
        return self.pool.close()  # type: ignore


class Connection:
    def __init__(self, con: asyncpg.Connection):
        self.con = con

    def transaction(self) -> Transaction:
        return self.con.transaction()

    async def execute(self, query: str, params: list[Any]) -> None:
        await self.con.execute(query, *params)

    async def fetchrow(self, query: str, params: list[Any]) -> dict | None:
        res = await self.con.fetchrow(query, *params)
        if res is not None:
            res = dict(res)
        assert res is None or isinstance(res, dict)
        return res

    async def fetchmany(self, query: str, params: list[Any]) -> list[dict]:
        return [dict(r) for r in await self.con.fetch(query, *params)]

    async def fetchval(self, query: str, params: list[Any]) -> Any:
        return await self.con.fetchval(query, *params)

    def cursor(self, query: str, params: list[Any]) -> CursorFactory:
        return self.con.cursor(query, *params)

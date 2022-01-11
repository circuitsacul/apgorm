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

from .utils.lazy_list import LazyList


class PoolAcquireContext:
    def __init__(self, pac: asyncpg.pool.PoolAcquireContext) -> None:
        self.pac = pac

    async def __aenter__(self) -> Connection:
        return Connection(await self.pac.__aenter__())

    async def __aexit__(self, *exc) -> None:
        await self.pac.__aexit__(*exc)


class Pool:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool

    def acquire(self) -> PoolAcquireContext:
        return PoolAcquireContext(self.pool.acquire())

    def close(self) -> Coroutine[Any, Any, None]:
        return self.pool.close()  # type: ignore


class Connection:
    """Wrapper around asyncpg.Connection."""

    def __init__(self, con: asyncpg.Connection) -> None:
        self.con = con

    def transaction(self) -> Transaction:
        """Enter a transaction.

        Usage:
        ```
        async with con.transaction():
            await con.execute("DROP TABLE users", [])
            raise Exception("Wait no I don't want to do that!")
        ```

        Alternatively:
        ```
        t = con.transaction()
        await t.start()
        await con.execute("DROP TABLE users", [])
        await t.rollback()

        # or, if you did want to do that, replace t.rollback() with t.commit():
        await t.commit()
        ```

        Returns:
            Transaction: The asyncpg.Transaction object.
        """

        return self.con.transaction()

    async def execute(
        self, query: str, params: list[Any] | None = None
    ) -> None:
        """Execute SQL.

        Consider using Database.execute() unless you want to manage the
        transaction flow.

        Args:
            query (str): The raw SQL.
            params (list[Any], optional): List of parameters. Defaults to None.
        """

        params = params or []
        await self.con.execute(query, *params)

    async def fetchrow(
        self, query: str, params: list[Any] | None = None
    ) -> dict | None:
        """Execute SQL and return a single row, if any.

        Consider using Database.fetchrow() unless you want to manage the
        transaction flow.

        Args:
            query (str): The raw SQL.
            params (list[Any], optional): List of parameters. Defaults to None.

        Returns:
            dict | None: The row or None.
        """

        params = params or []
        res = await self.con.fetchrow(query, *params)
        if res is not None:
            res = dict(res)
        assert res is None or isinstance(res, dict)
        return res

    async def fetchmany(
        self, query: str, params: list[Any] | None = None
    ) -> LazyList[asyncpg.Record, dict[str, Any]]:
        """Execute SQL, returning all found rows.

        See LazyList docs.

        Consider using Database.fetchmany() unless you want to manage the
        transaction flow.

        Args:
            query (str): The raw SQL.
            params (list[Any], optional): List of parameters. Defaults to None.

        Returns:
            LazyList[asyncpg.Record, dict[str, Any]]: [description]
        """

        params = params or []
        return LazyList(await self.con.fetch(query, *params), dict)

    async def fetchval(
        self, query: str, params: list[Any] | None = None
    ) -> Any:
        """Execute SQL, returning the values.

        For example:
        ```
        db.fetchrow("SELECT name FROM users")
        # -> {"name": "Circuit"}

        db.fetchval("SELECT name FROM users")
        # -> "Circuit"
        ```

        Args:
            query (str): [description]
            params (list[Any], optional): [description]. Defaults to None.

        Returns:
            Any: [description]
        """

        return await self.con.fetchval(query, *params)

    def cursor(
        self, query: str, params: list[Any] | None = None
    ) -> CursorFactory:
        """Returns a CursorFactory, but outside a transaction.

        Since cursors must be inside a transaction, you must handle the
        transaction flow like this:

        ```
        async with con.transaction():
            async for row in con.cursor():
                ...
        ```

        Args:
            query (str): The raw SQL
            params (list[Any], optional): List of parameters. Defaults to None.

        Returns:
            CursorFactory: The cursor factory.
        """

        params = params or []
        return self.con.cursor(query, *params)

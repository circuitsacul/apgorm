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

import pytest

from apgorm import Connection, LazyList, Pool


@pytest.fixture
def async_mocked_con(mocker):
    subcon = mocker.AsyncMock()
    subcon.fetchrow.return_value = {"hello": "world"}
    subcon.fetch.return_value = [{"hello": "world"}]
    subcon.fetchval.return_value = "hello, world"
    return subcon


@pytest.mark.asyncio
async def test_connection_execute(async_mocked_con):
    con = Connection(async_mocked_con)

    await con.execute("SELECT $1", [1])

    async_mocked_con.execute.assert_called_once_with("SELECT $1", 1)


@pytest.mark.asyncio
async def test_connection_fetchrow(async_mocked_con):
    con = Connection(async_mocked_con)

    res = await con.fetchrow("SELECT $1", [1])

    assert res == {"hello": "world"}
    async_mocked_con.fetchrow.assert_called_once_with("SELECT $1", 1)


@pytest.mark.asyncio
async def test_connection_fetchmany(async_mocked_con):
    con = Connection(async_mocked_con)

    res = await con.fetchmany("SELECT $1", [1])

    assert isinstance(res, LazyList)
    assert list(res) == [{"hello": "world"}]

    async_mocked_con.fetch.assert_called_once_with("SELECT $1", 1)


@pytest.mark.asyncio
async def test_connection_fetchval(async_mocked_con):
    con = Connection(async_mocked_con)

    res = await con.fetchval("SELECT $1", [1])

    assert res == "hello, world"
    async_mocked_con.fetchval.assert_called_once_with("SELECT $1", 1)


def test_connection_cursor(mocker):
    mocked_con = mocker.Mock()
    con = Connection(mocked_con)

    con.cursor("SELECT $1", [1])

    mocked_con.cursor.assert_called_once_with("SELECT $1", 1)


def test_connection_transaction(mocker):
    mocked_con = mocker.Mock()
    con = Connection(mocked_con)

    con.transaction()

    mocked_con.transaction.assert_called_once()


@pytest.mark.asyncio
async def test_pool(mocker, async_mocked_con):
    mocked_pac = mocker.AsyncMock()
    mocked_pac.__aenter__.return_value = async_mocked_con

    mocked_pool = mocker.Mock()
    mocked_pool.acquire.return_value = mocked_pac

    pool = Pool(mocked_pool)

    async with pool.acquire() as yielded_con:
        pass

    pool.close()

    assert yielded_con.con is async_mocked_con
    mocked_pool.acquire.assert_called_once()
    mocked_pool.close.assert_called_once()
    mocked_pac.__aenter__.assert_called_once()
    mocked_pac.__aexit__.assert_called_once()

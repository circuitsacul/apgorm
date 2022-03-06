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
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import asyncpg
import pytest
from pytest_mock import MockerFixture

import apgorm
from apgorm.types import VarChar


class User(apgorm.Model):
    name = VarChar(32).field()
    nick = VarChar(32).nullablefield()

    nick_unique = apgorm.Exclude((nick, "="), where="nick IS NOT NULL")

    primary_key = (name,)


class Database(apgorm.Database):
    users = User

    indexes = [apgorm.Index(User, User.nick)]


DB = Database(Path("tests/migrations"))


def test_updates_models_and_fields():
    assert DB.users.tablename == "users"
    assert DB.users.name.name == "name"
    assert DB.users.nick.name == "nick"
    assert DB.users.nick_unique.name == "nick_unique"
    assert DB.users.primary_key[0] is DB.users.name


def test_str_folder():
    STR = Database("tests/migrations")
    assert isinstance(STR._migrations_folder, Path)
    assert STR._migrations_folder == DB._migrations_folder


def test_collects_models():
    assert User in DB._all_models
    assert User is DB.users


def test_indexes_match():
    assert DB.indexes[0].table is DB.users
    assert DB.indexes[0].fields[0].name == "nick"


def test_describe():
    describe = DB.describe()

    assert len(describe.tables) == 2
    assert len(describe.indexes) == 1


@dataclass
class PatchedDBMethods:
    pool: Mock
    con: Mock
    curr: Mock


@pytest.fixture
def db(mocker: MockerFixture) -> PatchedDBMethods:
    def areturn(ret: Any = None) -> AsyncMock:
        func = mocker.AsyncMock()
        func.return_value = ret
        return func

    con = mocker.Mock()
    tc = mocker.AsyncMock()
    tc.__aenter__.return_value = None
    tc.__aexit__.return_value = None
    con.transaction.return_value = tc
    con.execute = areturn()
    con.fetchrow = areturn({"hello": "world"})
    con.fetchmany = areturn([{"hello": "world"}])
    con.fetchval = areturn("hello, world")

    curr = mocker.Mock()
    con.cursor.return_value = curr

    pool = mocker.Mock()
    pac = mocker.AsyncMock()
    pac.__aenter__.return_value = con
    pac.__aexit__.return_value = None
    pool.acquire.return_value = pac
    pool.close = areturn()

    mocker.patch.object(DB, "pool", pool)

    return PatchedDBMethods(pool, con, curr)


@pytest.mark.asyncio
async def test_connect(mocker: MockerFixture):
    cn = mocker.patch.object(asyncpg, "create_pool")
    fut = asyncio.Future()
    fut.set_result(None)
    cn.return_value = fut

    await DB.connect(hello="world")

    cn.assert_called_once_with(hello="world")
    assert DB.pool.pool is fut.result()


@pytest.mark.asyncio
async def test_cleanup(db: PatchedDBMethods):
    await DB.cleanup()

    db.pool.close.assert_called_once_with()


def assert_transaction(db: PatchedDBMethods):
    db.pool.acquire.assert_called_once_with()
    db.pool.acquire.return_value.__aenter__.assert_called_once_with()
    db.con.transaction.assert_called_once_with()
    db.con.transaction.return_value.__aenter__.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute(db: PatchedDBMethods):
    ret = await DB.execute("HELLO $1", ["world"])

    assert_transaction(db)
    db.con.execute.assert_called_once_with("HELLO $1", ["world"])
    assert ret is None


@pytest.mark.asyncio
async def test_fetchrow(db: PatchedDBMethods):
    ret = await DB.fetchrow("HELLO $1", ["world"])

    assert_transaction(db)
    db.con.fetchrow.assert_called_once_with("HELLO $1", ["world"])
    assert ret == db.con.fetchrow.return_value


@pytest.mark.asyncio
async def test_fetchmany(db: PatchedDBMethods):
    ret = await DB.fetchmany("HELLO $1", ["world"])

    assert_transaction(db)
    db.con.fetchmany.assert_called_once_with("HELLO $1", ["world"])
    assert ret == db.con.fetchmany.return_value


@pytest.mark.asyncio
async def test_fetchval(db: PatchedDBMethods):
    ret = await DB.fetchval("HELLO $1", ["world"])

    assert_transaction(db)
    db.con.fetchval.assert_called_once_with("HELLO $1", ["world"])
    assert ret == db.con.fetchval.return_value


@pytest.mark.asyncio
async def test_cursor(db: PatchedDBMethods):
    async with DB.cursor("HELLO $1", ["world"]) as curr:
        assert curr is db.curr

    assert_transaction(db)
    db.con.cursor.assert_called_once_with("HELLO $1", ["world"])


@pytest.mark.asyncio
async def test_cursor_with_con(db: PatchedDBMethods):
    async with DB.pool.acquire() as con:
        async with con.transaction():
            async with DB.cursor("HELLO $1", ["world"], con=db.con) as cursor:
                assert cursor is db.curr

    assert_transaction(db)
    db.con.cursor.assert_called_once_with("HELLO $1", ["world"])

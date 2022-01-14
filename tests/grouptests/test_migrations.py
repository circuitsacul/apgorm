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
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, Mock

import asyncpg
import pytest
from pytest_mock import MockerFixture

import apgorm
from apgorm.types import VarChar


class EmptyDB(apgorm.Database):
    pass


class User(apgorm.Model):
    name = VarChar(32).field()
    primary_key = (name,)


class UserDB(apgorm.Database):
    user = User

    indexes = [apgorm.Index(User, User.name)]


MIG_PATH = Path("tests/migrations")
EDB = EmptyDB(MIG_PATH)
UDB = UserDB(MIG_PATH)


def erase_migrations():
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)


@pytest.fixture
def patch_fetch(mocker: MockerFixture):
    ret = asyncio.Future()
    mock = mocker.Mock()
    mock.fetch_query.return_value.fetchmany.return_value = ret

    mocker.patch.object(UDB, "_migrations", mock)
    mocker.patch.object(EDB, "_migrations", mock)

    return ret, mock.fetch_query.return_value.fetchmany


@dataclass
class PatchedDBMethods:
    pool: Mock
    con: Mock
    curr: Mock


@pytest.fixture
def patch_pool(mocker: MockerFixture) -> PatchedDBMethods:
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

    mocker.patch.object(UDB, "pool", pool)
    mocker.patch.object(EDB, "pool", pool)
    mocker.patch.object(UDB._migrations.database, "pool", pool)
    mocker.patch.object(EDB._migrations.database, "pool", pool)

    return PatchedDBMethods(pool, con, curr)


@pytest.mark.asyncio
async def test_create_and_apply_migrations(patch_pool, mocker):
    erase_migrations()

    # Before migration creation
    assert not MIG_PATH.exists()
    assert len(EDB.load_all_migrations()) == 0
    assert EDB.load_last_migration() is None
    assert EDB.must_create_migrations()

    # Create migrations
    EDB.create_migrations()
    assert not EDB.must_create_migrations()
    assert UDB.must_create_migrations()

    UDB.create_migrations()
    assert EDB.must_create_migrations()
    assert not UDB.must_create_migrations()

    EDB.create_migrations()
    UDB.create_migrations()

    # Test trying to create migration when none are needed
    with pytest.raises(apgorm.exceptions.NoMigrationsToCreate):
        UDB.create_migrations()

    # Test with override
    UDB.create_migrations(allow_empty=True)

    # After creation (there should be three, the last should be empty)
    assert MIG_PATH.exists()
    assert len(EDB.load_all_migrations()) == 5
    assert EDB.load_last_migration().migration_id == 4

    assert EDB.load_migration_from_id(1).migration_id == 1

    assert (
        EDB.load_migration_from_id(3).describe
        == EDB.load_migration_from_id(4).describe
    )
    assert EDB.load_migration_from_id(4).migrations == ""

    # test applying the three migrations
    def _make_fut(
        ret: Any | None = None, exc: Any | None = None
    ) -> asyncio.Future:
        fut = asyncio.Future()
        if exc:
            fut.set_exception(exc)
        else:
            fut.set_result(ret)
        return fut

    # patch _migrations.fetch
    f = mocker.patch.object(UDB, "_migrations")
    f.return_value.create.return_value = _make_fut()
    f.fetch.return_value = _make_fut(
        exc=apgorm.exceptions.ModelNotFound(User, {})
    )

    mig = mocker.Mock()
    mig.id_.v = 0
    f.fetch_query.return_value.fetchmany.return_value = _make_fut([mig])

    await UDB.apply_migrations()


@pytest.mark.asyncio
async def test_load_unapplied_none(patch_fetch: tuple[asyncio.Future, Mock]):
    erase_migrations()
    ret, func = patch_fetch
    ret.set_result([])

    UDB.create_migrations()

    assert (
        am := UDB.load_all_migrations()
    ) == await UDB.load_unapplied_migrations()
    assert len(am) == 1
    assert am[0].migration_id == 0


@pytest.mark.asyncio
async def test_load_unapplied_all(
    patch_fetch: tuple[asyncio.Future, Mock],
    mocker: MockerFixture,
):
    erase_migrations()
    ret, func = patch_fetch
    mig = mocker.Mock()
    mig.id_.v = 0
    ret.set_result([mig])

    assert len(await UDB.load_unapplied_migrations()) == 0


@pytest.mark.asyncio
async def test_load_unapplied_exc(
    patch_fetch: tuple[asyncio.Future, Mock],
):
    erase_migrations()
    UDB.create_migrations()

    ret, func = patch_fetch
    ret.set_exception(asyncpg.UndefinedTableError)

    assert len(await UDB.load_unapplied_migrations()) == 1
    func.assert_called_once_with()


@pytest.mark.asyncio
async def test_must_apply_true(patch_fetch: tuple[asyncio.Future, Mock]):
    erase_migrations()
    UDB.create_migrations()

    ret, func = patch_fetch
    ret.set_result([])

    assert await UDB.must_apply_migrations()


@pytest.mark.asyncio
async def test_must_apply_false(
    patch_fetch: tuple[asyncio.Future, Mock],
    mocker: MockerFixture,
):
    erase_migrations()
    UDB.create_migrations()

    ret, func = patch_fetch
    mig = mocker.Mock()
    mig.id_.v = 0
    ret.set_result([mig])

    assert not await UDB.must_apply_migrations()


@pytest.mark.asyncio
async def test_apply_migrations(
    mocker: MockerFixture,
    patch_fetch: tuple[asyncio.Future, Mock],
):
    erase_migrations()
    UDB.create_migrations()

    ret, _ = patch_fetch
    ret.set_result([])
    func = mocker.patch.object(UDB, "_apply_migration")
    func.return_value = asyncio.Future()
    func.return_value.set_result(None)

    await UDB.apply_migrations()

    func.assert_called_once()

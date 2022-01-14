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
from pathlib import Path
from unittest.mock import Mock

import asyncpg
import pytest
from pytest_mock import MockerFixture

import apgorm
from apgorm.types import VarChar


class User(apgorm.Model):
    name = VarChar(32).field()
    primary_key = (name,)


class Database(apgorm.Database):
    users = User


@pytest.fixture
def db():
    DB = Database(Path("tests/migrations"))
    if DB._migrations_folder.exists():
        shutil.rmtree(DB._migrations_folder)
    if DB.must_create_migrations():
        DB.create_migrations()
    return DB


@pytest.fixture
def patch_fetch(mocker: MockerFixture, db: Database):
    ret = asyncio.Future()
    mock = mocker.Mock()
    mock.fetch_query.return_value.fetchmany.return_value = ret
    db._migrations = mock
    return ret, mock.fetch_query.return_value.fetchmany


@pytest.mark.asyncio
async def test_load_unapplied_none(
    patch_fetch: tuple[asyncio.Future, Mock], db: Database
):
    ret, func = patch_fetch
    ret.set_result([])

    assert (
        am := db.load_all_migrations()
    ) == await db.load_unapplied_migrations()
    assert len(am) == 1
    assert am[0].migration_id == 0


@pytest.mark.asyncio
async def test_load_unapplied_all(
    patch_fetch: tuple[asyncio.Future, Mock],
    db: Database,
    mocker: MockerFixture,
):
    ret, func = patch_fetch
    mig = mocker.Mock()
    mig.id_.v = 0
    ret.set_result([mig])

    assert len(await db.load_unapplied_migrations()) == 0


@pytest.mark.asyncio
async def test_load_unapplied_exc(
    patch_fetch: tuple[asyncio.Future, Mock],
    db: Database,
    mocker: MockerFixture,
):
    ret, func = patch_fetch
    ret.set_exception(asyncpg.UndefinedTableError)

    assert len(await db.load_unapplied_migrations()) == 1
    func.assert_called_once_with()


@pytest.mark.asyncio
async def test_must_apply_true(
    patch_fetch: tuple[asyncio.Future, Mock], db: Database
):
    ret, func = patch_fetch
    ret.set_result([])

    assert await db.must_apply_migrations()


@pytest.mark.asyncio
async def test_must_apply_false(
    patch_fetch: tuple[asyncio.Future, Mock],
    db: Database,
    mocker: MockerFixture,
):
    ret, func = patch_fetch
    mig = mocker.Mock()
    mig.id_.v = 0
    ret.set_result([mig])

    assert not await db.must_apply_migrations()


@pytest.mark.asyncio
async def test_apply_migrations(
    db: Database,
    mocker: MockerFixture,
    patch_fetch: tuple[asyncio.Future, Mock],
):
    ret, _ = patch_fetch
    ret.set_result([])
    func = mocker.patch.object(db, "_apply_migration")
    func.return_value = asyncio.Future()
    func.return_value.set_result(None)

    await db.apply_migrations()

    func.assert_called_once()

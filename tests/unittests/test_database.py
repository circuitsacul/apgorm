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


MIG_PATH = Path("tests/migrations")
if MIG_PATH.exists():
    shutil.rmtree(MIG_PATH)
DB = Database(MIG_PATH)


def test_updates_models_and_fields():
    assert DB.users.tablename == "users"
    assert DB.users.name.name == "name"
    assert DB.users.nick.name == "nick"
    assert DB.users.nick_unique.name == "nick_unique"
    assert DB.users.primary_key[0] is DB.users.name


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


def test_load_all_migrations(mocker: MockerFixture):
    lam = mocker.patch(
        "apgorm.migrations.migration.Migration._load_all_migrations"
    )
    lam.return_value = (m := [mocker.Mock(), mocker.Mock()])

    assert DB.load_all_migrations() == m
    lam.assert_called_once_with(DB._migrations_folder)


def test_load_last_migration(mocker: MockerFixture):
    lam = mocker.patch(
        "apgorm.migrations.migration.Migration._load_all_migrations"
    )
    migrations = []
    for i in [0, 1, 9, 3, 2]:
        m = mocker.Mock()
        m.migration_id = i
        migrations.append(m)
    lam.return_value = migrations

    lm = DB.load_last_migration()
    assert lm is not None
    assert lm.migration_id == 9
    lam.assert_called_once_with(DB._migrations_folder)


def test_load_from_id(mocker: MockerFixture):
    fp = mocker.patch("apgorm.migrations.migration.Migration._from_path")
    fp.return_value = mocker.Mock()
    get_path_spy = mocker.spy(apgorm.Migration, "_path_from_id")

    res = DB.load_migration_from_id(16)

    assert res is fp.return_value
    get_path_spy.assert_called_once_with(16, DB._migrations_folder)
    fp.assert_called_once_with(DB._migrations_folder / str(16))


def test_must_create_migrations_false(mocker: MockerFixture):
    func = mocker.patch.object(DB, "_create_next_migration")
    func.return_value = None

    assert not DB.must_create_migrations()
    func.assert_called_once()


def test_must_create_igrations_true(mocker: MockerFixture):
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)

    spy = mocker.spy(DB, "_create_next_migration")

    assert DB.must_create_migrations()
    spy.assert_called_once()


def test_create_migrations():
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)
    mig = DB.create_migrations()

    assert MIG_PATH.exists()
    assert not DB.must_create_migrations()
    assert mig.migration_id == 0


def test_create_migrations_none_to_create(mocker: MockerFixture):
    func = mocker.patch.object(DB, "must_create_migrations")
    func.return_value = False

    try:
        DB.create_migrations()
    except apgorm.exceptions.NoMigrationsToCreate:
        pass
    else:
        assert False, "Didn't raise NoMigrationsToCreate"


def test_create_migrations_none_to_create_allow_empty(mocker: MockerFixture):
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)

    func = mocker.patch.object(DB, "must_create_migrations")
    func.return_value = False
    func = mocker.patch.object(DB, "_create_next_migration")
    func.return_value = ""

    mig = DB.create_migrations(allow_empty=True)

    assert mig.migrations == ""


@pytest.mark.asyncio
async def test_must_apply_migrations_false(mocker: MockerFixture):
    func = mocker.patch.object(DB, "load_unapplied_migrations")
    func.return_value = []

    assert not await DB.must_apply_migrations()


@pytest.mark.asyncio
async def test_must_apply_migrations_true(mocker: MockerFixture):
    func = mocker.patch.object(DB, "load_unapplied_migrations")
    func.return_value = [mocker.Mock()]

    assert await DB.must_apply_migrations()


@pytest.mark.asyncio
async def test_load_unapplied_migrations(mocker: MockerFixture):
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)

    DB.create_migrations()

    m = mocker.Mock()
    ret = asyncio.Future()

    migration = mocker.Mock()
    ret.set_result([migration])

    mocker.patch.object(DB, "_migrations", m)
    m.fetch_query.return_value.fetchmany.return_value = ret

    unapplied = await DB.load_unapplied_migrations()
    all_mig = DB.load_all_migrations()

    assert unapplied == all_mig
    m.fetch_query.return_value.fetchmany.assert_called_once_with()

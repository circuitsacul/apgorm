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

from dataclasses import dataclass
from enum import IntEnum
from typing import Any
from unittest.mock import AsyncMock, Mock

import pytest
from pytest_mock import MockerFixture

import apgorm
from apgorm.types import Int, Serial, VarChar


class UserStatus(IntEnum):
    OFFLINE = 0
    INVISIBLE = 1
    ONLINE = 2
    DND = 3


def validate_status(value) -> bool:
    assert isinstance(value, UserStatus)
    return True


class User(apgorm.Model):
    userid = Serial().field()
    name = VarChar(32).field()
    nick = VarChar(32).nullablefield()
    status = (
        Int()
        .field(default=0)
        .with_converter(apgorm.IntEFConverter(UserStatus))
    )
    status.add_validator(lambda v: v is not UserStatus.INVISIBLE)
    default_fact = VarChar(32).field(default_factory=lambda: "hello, world")

    name_unique = apgorm.Unique(name)
    primary_key = (userid,)

    games = apgorm.ManyToMany(
        "userid", "players.userid", "players.gameid", "games.gameid"
    )


class Game(apgorm.Model):
    gameid = Serial().field()

    users = apgorm.ManyToMany(
        "gameid", "players.gameid", "players.userid", "users.userid"
    )

    primary_key = (gameid,)


class Player(apgorm.Model):
    userid = Int().field()
    gameid = Int().field()

    uid_fk = apgorm.ForeignKey(userid, User.userid)
    gid_fk = apgorm.ForeignKey(gameid, Game.gameid)

    primary_key = (
        userid,
        gameid,
    )


class Database(apgorm.Database):
    users = User
    games = Game
    players = Player


DB = Database(None)


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


def assert_transaction(db: PatchedDBMethods):
    db.pool.acquire.assert_called_once_with()
    db.pool.acquire.return_value.__aenter__.assert_called_once_with()
    db.con.transaction.assert_called_once_with()
    db.con.transaction.return_value.__aenter__.assert_called_once_with()


def test_attr_copies():
    user = User()

    for name, field in user.all_fields.items():
        assert field is getattr(user, name)
        assert field.name == name
        assert getattr(user, name).name == name
        assert [pk is user.all_fields[pk.name] for pk in user.primary_key]

        assert field is not User.all_fields[name]
        assert User.all_fields[name] is getattr(User, name)
        assert [pk is User.all_fields[pk.name] for pk in User.primary_key]

    for name, constraint in user.all_constraints.items():
        assert constraint is getattr(user, name)
        assert constraint.name == name
        assert getattr(user, name).name == name

        assert constraint is User.all_constraints[name]
        assert User.all_constraints[name] is getattr(User, name)

    for name, mtm in user._all_mtm.items():
        assert mtm is not getattr(user, name)
        assert mtm is getattr(User, name)
        assert getattr(User, name) is User._all_mtm[name]


def test_converter_field_in_init():
    user = User(status=UserStatus.OFFLINE)
    assert user.status.v is UserStatus.OFFLINE
    assert user.status._value == UserStatus.OFFLINE.value


def test_validate_in_init():
    with pytest.raises(apgorm.exceptions.InvalidFieldValue):
        User(status=UserStatus.INVISIBLE)

    User(status=UserStatus.OFFLINE)
    User(True, status=UserStatus.INVISIBLE)


def test_gets_default():
    user = User()

    assert user.status.v is UserStatus.OFFLINE
    assert user.default_fact.v == "hello, world"
    assert user.name._value is apgorm.UNDEF.UNDEF


@pytest.mark.asyncio
async def test_delete(db: PatchedDBMethods, mocker: MockerFixture):
    async def new_execute(self: apgorm.DeleteQueryBuilder):
        assert self._where_logic().render_no_params() == "userid = $1"
        return [User(userid=1)]

    mocker.patch.object(apgorm.DeleteQueryBuilder, "execute", new_execute)

    user = User(userid=5)
    ret = await user.delete()
    assert ret.userid.v == 1
    assert user.userid.v == 5


@pytest.mark.asyncio
async def test_delete_none(db: PatchedDBMethods, mocker: MockerFixture):
    async def new_execute(self: apgorm.DeleteQueryBuilder):
        return []

    mocker.patch.object(apgorm.DeleteQueryBuilder, "execute", new_execute)

    user = User(userid=5)
    with pytest.raises(apgorm.exceptions.ModelNotFound):
        await user.delete()


@pytest.mark.asyncio
async def test_save_normal(db: PatchedDBMethods, mocker: MockerFixture):
    async def new_execute(self: apgorm.UpdateQueryBuilder):
        assert self._where_logic().render() == (
            "userid = $1",
            [1],
        )
        set_values = self._set_values
        assert [
            (
                k.render_no_params(),
                v,
            )
            for k, v in set_values.items()
        ] == [("name", "New Name")]
        return [User(userid=5)]

    mocker.patch.object(apgorm.UpdateQueryBuilder, "execute", new_execute)

    user = User(userid=1)
    user.name.v = "New Name"
    await user.save()

    assert user.userid.v == 5  # updated


@pytest.mark.asyncio
async def test_save_none_to_save(db: PatchedDBMethods, mocker: MockerFixture):
    spy = mocker.spy(apgorm.UpdateQueryBuilder, "execute")
    user = User(userid=5)
    await user.save()

    spy.assert_not_called()

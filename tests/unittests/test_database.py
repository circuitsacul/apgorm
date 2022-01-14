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

from pathlib import Path

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

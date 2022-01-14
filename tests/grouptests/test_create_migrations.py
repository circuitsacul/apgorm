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

import shutil
from pathlib import Path

import pytest

import apgorm
from apgorm.types import VarChar


class EmptyDB(apgorm.Database):
    pass


class User(apgorm.Model):
    name = VarChar(32).field()
    primary_key = (name,)


class UserDB(apgorm.Database):
    user = User


MIG_PATH = Path("tests/migrations")
EDB = EmptyDB(MIG_PATH)
UDB = UserDB(MIG_PATH)


def test_migrations():
    if MIG_PATH.exists():
        shutil.rmtree(MIG_PATH)

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

    # Test trying to create migration when none are needed
    with pytest.raises(apgorm.exceptions.NoMigrationsToCreate):
        UDB.create_migrations()

    # Test with override
    UDB.create_migrations(allow_empty=True)

    # After creation (there should be three, the last should be empty)
    assert MIG_PATH.exists()
    assert len(EDB.load_all_migrations()) == 3
    assert EDB.load_last_migration().migration_id == 2

    assert EDB.load_migration_from_id(1).migration_id == 1

    assert (
        EDB.load_migration_from_id(1).describe
        == EDB.load_migration_from_id(2).describe
    )
    assert EDB.load_migration_from_id(2).migrations == ""

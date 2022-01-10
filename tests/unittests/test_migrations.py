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

import warnings

import asyncpg
import pytest

from tests.database import Database


def _test_create(db: Database):
    assert db.must_create_migrations()
    db.create_migrations()
    assert not db.must_create_migrations()


async def _test_apply(db: Database):
    assert await db.must_apply_migrations()
    await db.apply_migrations()
    assert not await db.must_apply_migrations()

    # test that all fields for primar


@pytest.mark.asyncio
async def test_migrations(db: Database):
    try:
        await db._migrations.fetch_query().fetchmany()
    except asyncpg.UndefinedTableError:
        pass
    else:
        warnings.warn(
            "Unable to test migrations. Please delete and recreate the"
            "`apgorm_testing_database` database."
        )
        return

    # initial migration
    _test_create(db)
    await _test_apply(db)

    # test dropping everything
    _orig_models = db._all_models
    _orig_indexes = db.indexes

    db._all_models = [db._migrations]  # we need to keep this table
    db.indexes = []

    _test_create(db)
    await _test_apply(db)

    # test adding everything back
    db._all_models = _orig_models
    db.indexes = _orig_indexes

    _test_create(db)
    await _test_apply(db)

    # make sure migrations exist
    assert len(db.load_all_migrations()) == 3
    lm = db.load_last_migration()
    assert lm is not None
    assert lm.migration_id == 2

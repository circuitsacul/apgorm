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

from typing import TYPE_CHECKING

import asyncpg

from apgorm.exceptions import MigrationAlreadyApplied, ModelNotFound

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.database import Database

    from .migration import Migration


async def apply_migration(migration: Migration, db: Database) -> None:
    try:
        await db._migrations.fetch(id_=migration.migration_id)
    except (asyncpg.exceptions.UndefinedTableError, ModelNotFound):
        pass
    else:
        raise MigrationAlreadyApplied(str(migration.path))

    assert db.pool is not None
    async with db.pool.acquire() as con:
        async with con.transaction():
            await con.execute(migration.migrations, [])
            await db._migrations(id_=migration.migration_id).create(con=con)

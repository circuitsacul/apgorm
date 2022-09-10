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

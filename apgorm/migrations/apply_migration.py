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

from apgorm.exceptions import ModelNotFound
from apgorm.sql.generators import alter, comp, query
from apgorm.sql.generators.helpers import r

if TYPE_CHECKING:
    from apgorm.connection import Connection
    from apgorm.database import Database

    from .migration import Migration


async def apply_migration(migration: Migration, db: Database):
    try:
        await db._migrations.fetch(id_=migration.migration_id)
    except (asyncpg.exceptions.UndefinedTableError, ModelNotFound):
        pass
    else:
        raise Exception("Migration already applied.")

    assert db.pool is not None
    async with db.pool.acquire() as con:
        async with con.transaction():
            await _apply_migration(migration, con)

    # mark that the migration was applied
    await db._migrations(id_=migration.migration_id).create()


async def _apply_migration(migration: Migration, con: Connection):
    # add tables
    for new_table in migration.new_tables:
        await con.execute(*alter.add_table(r(new_table)).render())

    # drop tables
    for drop_table in migration.dropped_tables:
        await con.execute(*alter.drop_table(r(drop_table)).render())

    # add fields
    for new_field in migration.new_fields:
        await con.execute(
            *alter.add_field(
                r(new_field.table),
                r(new_field.name),
                r(new_field.type_),
            ).render()
        )
        if new_field.default is not None:
            await con.execute(
                *alter.set_field_default(
                    r(new_field.table),
                    r(new_field.name),
                    r(new_field.default),
                ).render()
            )

    # drop constraints
    for drop_constraint in migration.dropped_constraints:
        await con.execute(
            *alter.drop_constraint(
                r(drop_constraint.table),
                r(drop_constraint.name),
            ).render()
        )

    # drop fields
    for drop_field in migration.dropped_fields:
        await con.execute(
            *alter.drop_field(
                r(drop_field.table),
                r(drop_field.name),
            ).render()
        )

    # field not nulls
    for alter_not_null in migration.field_not_nulls:
        if alter_not_null.one_time_default is not None:
            await con.execute(
                *query.update(
                    r(alter_not_null.table),
                    {r(alter_not_null.field): alter_not_null.one_time_default},
                    comp.is_null(r(alter_not_null.field)),
                ).render()
            )
        await con.execute(
            *alter.set_field_not_null(
                r(alter_not_null.table),
                r(alter_not_null.field),
                alter_not_null.not_null,
            ).render()
        )

    # add constraints
    new_constraints = (
        migration.new_unique_constraints
        + migration.new_pk_constraints
        + migration.new_check_constraints
        + migration.new_fk_constraints
    )
    for new_constraint in new_constraints:
        await con.execute(
            *alter.add_constraint(
                r(new_constraint.table),
                new_constraint.raw_sql,
            ).render()
        )

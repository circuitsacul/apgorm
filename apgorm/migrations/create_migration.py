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
from typing import TYPE_CHECKING

from apgorm.sql.generators import alter
from apgorm.sql.sql import r
from apgorm.undefined import UNDEF

from .describe import DescribeConstraint
from .migration import Migration

if TYPE_CHECKING:  # pragma: no cover
    from .describe import Describe


def _handle_constraint_list(
    tablename: str,
    orig: list[DescribeConstraint],
    curr: list[DescribeConstraint],
) -> tuple[list[str], list[str]]:
    origd = {c.name: c for c in orig}
    currd = {c.name: c for c in curr}

    new_constraints = [
        alter.add_constraint(
            r(tablename),
            c.raw_sql,
        ).render_no_params()
        for c in currd.values()
        if c.name not in origd
    ]
    drop_constraints = [
        alter.drop_constraint(r(tablename), r(c.name)).render_no_params()
        for c in origd.values()
        if c.name not in currd
    ]

    common = [(currd[k], origd[k]) for k in currd.keys() & origd.keys()]
    for currc, origc in common:
        if currc.raw_sql == origc.raw_sql:
            continue

        new_constraints.append(
            alter.add_constraint(
                r(tablename), currc.raw_sql
            ).render_no_params()
        )
        drop_constraints.append(
            alter.drop_constraint(
                r(tablename),
                r(currc.name),
            ).render_no_params()
        )

    return new_constraints, drop_constraints


def create_next_migration(cd: Describe, folder: Path) -> str | None:
    lm = Migration._load_last_migration(folder)

    curr_tables = {t.name: t for t in cd.tables}
    last_tables = {t.name: t for t in lm.describe.tables} if lm else {}

    migrations: list[str] = []

    # tables  # TODO: renamed tables
    add_tables = [
        alter.add_table(r(key)).render_no_params()
        for key in curr_tables
        if key not in last_tables
    ]
    drop_tables = [
        alter.drop_table(r(key)).render_no_params()
        for key in last_tables
        if key not in curr_tables
    ]

    # everything else
    curr_indexes = {c.name: c for c in cd.indexes}
    last_indexes = {c.name: c for c in lm.describe.indexes} if lm else {}
    comm_indexes = [
        (curr_indexes[k], last_indexes[k])
        for k in curr_indexes.keys() & last_indexes.keys()
    ]
    add_indexes: list[str] = [
        alter.add_index(c.raw_sql).render_no_params()
        for name, c in curr_indexes.items()
        if name not in last_indexes
    ]
    drop_indexes: list[str] = [
        alter.drop_index(r(c.name)).render_no_params()
        for name, c in last_indexes.items()
        if name not in curr_indexes
    ]
    for curr, last in comm_indexes:
        if curr.raw_sql != last.raw_sql:
            drop_indexes.append(
                alter.drop_index(r(curr.name)).render_no_params()
            )
            add_indexes.append(
                alter.add_index(curr.raw_sql).render_no_params()
            )

    add_unique_constraints: list[str] = []
    add_pk_constraints: list[str] = []
    add_check_constraints: list[str] = []
    add_fk_constraints: list[str] = []
    add_exclude_constraints: list[str] = []

    drop_unique_constraints: list[str] = []
    drop_pk_constraints: list[str] = []
    drop_check_constraints: list[str] = []
    drop_fk_constraints: list[str] = []
    drop_exclude_constraints: list[str] = []

    add_fields: list[str] = []
    drop_fields: list[str] = []

    field_not_nulls: list[str] = []

    for tablename, currtable in curr_tables.items():
        lasttable = (
            last_tables[tablename] if tablename in last_tables else None
        )

        # fields:
        curr_fields = {f.name: f for f in currtable.fields}
        last_fields = (
            {f.name: f for f in lasttable.fields} if lasttable else {}
        )

        add_fields.extend(
            [
                alter.add_field(
                    r(tablename), r(key), r(f.type_)
                ).render_no_params()
                for key, f in curr_fields.items()
                if key not in last_fields
            ]
        )
        drop_fields.extend(
            [
                alter.drop_field(r(tablename), r(key)).render_no_params()
                for key, f in last_fields.items()
                if key not in curr_fields
            ]
        )

        # field not nulls:
        for field in curr_fields.values():
            last_not_null = (
                UNDEF.UNDEF
                if field.name not in last_fields
                else last_fields[field.name].not_null
            )
            set_nn_to: bool | None = None
            if last_not_null is UNDEF.UNDEF:
                if field.not_null is True:
                    set_nn_to = True
            elif last_not_null != field.not_null:
                set_nn_to = field.not_null

            if set_nn_to is not None:
                field_not_nulls.append(
                    alter.set_field_not_null(
                        r(tablename),
                        r(field.name),
                        set_nn_to,
                    ).render_no_params()
                )

        # constraints (in the order they should be applied)
        _new, _drop = _handle_constraint_list(
            tablename,
            lasttable.unique_constraints if lasttable else [],
            currtable.unique_constraints,
        )
        add_unique_constraints.extend(_new)
        drop_unique_constraints.extend(_drop)

        _new, _drop = _handle_constraint_list(
            tablename,
            [lasttable.pk_constraint] if lasttable else [],
            [currtable.pk_constraint],
        )
        add_pk_constraints.extend(_new)
        drop_pk_constraints.extend(_drop)

        _new, _drop = _handle_constraint_list(
            tablename,
            lasttable.check_constraints if lasttable else [],
            currtable.check_constraints,
        )
        add_check_constraints.extend(_new)
        drop_check_constraints.extend(_drop)

        _new, _drop = _handle_constraint_list(
            tablename,
            lasttable.fk_constraints if lasttable else [],
            currtable.fk_constraints,
        )
        add_fk_constraints.extend(_new)
        drop_fk_constraints.extend(_drop)

        _new, _drop = _handle_constraint_list(
            tablename,
            lasttable.exclude_constraints if lasttable else [],
            currtable.exclude_constraints,
        )
        add_exclude_constraints.extend(_new)
        drop_exclude_constraints.extend(_drop)

    for tablename, lasttable in last_tables.items():
        if tablename in curr_tables:
            continue
        _, _drop = _handle_constraint_list(
            tablename,
            lasttable.fk_constraints,
            [],
        )
        drop_fk_constraints.extend(_drop)

    # finalization
    migrations.extend(add_tables)

    migrations.extend(drop_fk_constraints)

    migrations.extend(drop_indexes)

    migrations.extend(drop_tables)

    migrations.extend(add_fields)

    migrations.extend(drop_pk_constraints)
    migrations.extend(drop_unique_constraints)
    migrations.extend(drop_check_constraints)
    migrations.extend(drop_exclude_constraints)

    migrations.extend(drop_fields)

    migrations.extend(field_not_nulls)

    migrations.extend(add_indexes)

    migrations.extend(add_unique_constraints)
    migrations.extend(add_check_constraints)
    migrations.extend(add_pk_constraints)
    migrations.extend(add_fk_constraints)
    migrations.extend(add_exclude_constraints)

    if len(migrations) == 0:
        return None
    return ";\n".join(migrations) + ";"

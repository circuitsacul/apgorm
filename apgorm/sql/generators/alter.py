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

from typing import Any

from apgorm.sql.sql import SQL, Block, Renderer

from .helpers import r


def add_table(tablename: Block) -> Block:
    return Block(r("CREATE TABLE"), tablename, r("()"))


def drop_table(tablename: Block) -> Block:
    return Block(r("DROP TABLE"), tablename)


def _alter_table(tablename: Block, sql: SQL) -> Block:
    return Block(r("ALTER TABLE"), tablename, sql)


def add_table_constraint(
    tablename: Block,
    constraint_raw_sql: str,
    constraint_params: list[Any],
) -> tuple[str, list]:  # kinda a hack but it works
    b = _alter_table(tablename, Block(r("ADD")))
    renderer = Renderer()
    renderer._curr_value_id = len(constraint_params)
    raw_sql, params = renderer.render(b)

    return f"{raw_sql} {constraint_raw_sql}", constraint_params + params


def drop_table_constraint(tablename: Block, constraint_name: Block) -> Block:
    return _alter_table(
        tablename, Block(r("DROP CONSTRAINT"), constraint_name)
    )


def add_field(tablename: Block, fieldname: Block, type_: Block) -> Block:
    return _alter_table(
        tablename,
        Block(
            r("ADD COLUMN"),
            fieldname,
            type_,
        ),
    )


def drop_field(tablename: Block, fieldname: Block) -> Block:
    return _alter_table(tablename, Block(r("DROP COLUMN"), fieldname))


def _alter_field(tablename: Block, fieldname: Block, sql: SQL) -> Block:
    return _alter_table(
        tablename,
        Block(
            r("ALTER COLUMN"),
            fieldname,
            sql,
        ),
    )

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

from apgorm.sql.sql import SQL, Block, r


def add_table(tablename: Block) -> Block:
    return Block(r("CREATE TABLE"), tablename, r("()"))


def drop_table(tablename: Block) -> Block:
    return Block(r("DROP TABLE"), tablename)


def add_index(raw_sql: str) -> Block:
    return Block(r("CREATE"), r(raw_sql))


def drop_index(name: Block) -> Block:
    return Block(r("DROP INDEX"), name)


def _alter_table(tablename: Block, sql: SQL) -> Block:
    return Block(r("ALTER TABLE"), tablename, sql)


def add_constraint(
    tablename: Block,
    constraint_raw_sql: str,
) -> Block:
    return _alter_table(tablename, Block(r("ADD"), r(constraint_raw_sql)))


def drop_constraint(tablename: Block, constraint_name: Block) -> Block:
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


def set_field_not_null(
    tablename: Block, fieldname: Block, not_null: bool
) -> Block:
    return _alter_field(
        tablename,
        fieldname,
        Block(
            r("SET NOT NULL") if not_null else r("DROP NOT NULL"),
        ),
    )

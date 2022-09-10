from __future__ import annotations

from typing import Any

from apgorm.sql.sql import SQL, Block, raw


def add_table(tablename: Block[Any]) -> Block[Any]:
    return Block(raw("CREATE TABLE"), tablename, raw("()"))


def drop_table(tablename: Block[Any]) -> Block[Any]:
    return Block(raw("DROP TABLE"), tablename)


def add_index(raw_sql: str) -> Block[Any]:
    return Block(raw("CREATE"), raw(raw_sql))


def drop_index(name: Block[Any]) -> Block[Any]:
    return Block(raw("DROP INDEX"), name)


def _alter_table(tablename: Block[Any], sql: SQL[Any]) -> Block[Any]:
    return Block(raw("ALTER TABLE"), tablename, sql)


def add_constraint(
    tablename: Block[Any], constraint_raw_sql: str
) -> Block[Any]:
    return _alter_table(tablename, Block(raw("ADD"), raw(constraint_raw_sql)))


def drop_constraint(
    tablename: Block[Any], constraint_name: Block[Any]
) -> Block[Any]:
    return _alter_table(
        tablename, Block(raw("DROP CONSTRAINT"), constraint_name)
    )


def add_field(
    tablename: Block[Any], fieldname: Block[Any], type_: Block[Any]
) -> Block[Any]:
    return _alter_table(tablename, Block(raw("ADD COLUMN"), fieldname, type_))


def drop_field(tablename: Block[Any], fieldname: Block[Any]) -> Block[Any]:
    return _alter_table(tablename, Block(raw("DROP COLUMN"), fieldname))


def _alter_field(
    tablename: Block[Any], fieldname: Block[Any], sql: SQL[Any]
) -> Block[Any]:
    return _alter_table(tablename, Block(raw("ALTER COLUMN"), fieldname, sql))


def set_field_not_null(
    tablename: Block[Any], fieldname: Block[Any], not_null: bool
) -> Block[Any]:
    return _alter_field(
        tablename,
        fieldname,
        Block(raw("SET NOT NULL") if not_null else raw("DROP NOT NULL")),
    )

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

from typing import TYPE_CHECKING, Any, Literal, Sequence, Type, overload

from apgorm.field import BaseField
from apgorm.sql.sql import SQL, Block, join, raw, wrap
from apgorm.types.boolean import Bool
from apgorm.undefined import UNDEF

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.model import Model


@overload
def select(
    *,
    from_: Model | Type[Model] | Block[Any],
    fields: Sequence[BaseField[Any, Any, Any] | Block[Any]] | None = ...,
    where: Block[Bool] | None = ...,
    order_by: SQL[Any] | UNDEF = ...,
    reverse: bool = ...,
    limit: int | None = ...,
) -> Block[Any]:
    ...


@overload
def select(
    *,
    from_: Model | Type[Model] | Block[Any],
    count: Literal[True] = True,
    where: Block[Bool] | None = ...,
    limit: int | None = ...,
) -> Block[Any]:
    ...


def select(
    *,
    from_: Model | Type[Model] | Block[Any],
    fields: Sequence[BaseField[Any, Any, Any] | Block[Any]] | None = None,
    count: bool = False,
    where: Block[Bool] | None = None,
    order_by: SQL[Any] | UNDEF = UNDEF.UNDEF,
    reverse: bool = False,
    limit: int | None = None,
) -> Block[Any]:
    sql = Block[Any](raw("SELECT"))

    if count:
        sql += Block(raw("COUNT(1)"))
    elif fields is not None:
        sql += join(raw(","), *fields, wrap=True)
    else:
        sql += Block(raw("*"))

    tablename = from_ if isinstance(from_, Block) else raw(from_.tablename)
    sql += Block(raw("FROM"), tablename)

    if where is not None:
        sql += Block(raw("WHERE"), wrap(where))

    if order_by is not UNDEF.UNDEF:
        sql += Block(raw("ORDER BY"), order_by)
        sql += raw("DESC" if reverse else "ASC")

    if limit is not None:
        sql += Block(raw("LIMIT"), raw(str(limit)))

    return wrap(sql)


def delete(
    from_: Model | Type[Model] | Block[Any],
    where: Block[Bool] | None = None,
    return_fields: Sequence[BaseField[Any, Any, Any] | Block[Any]]
    | None = None,
) -> Block[Any]:
    tablename = from_ if isinstance(from_, Block) else raw(from_.tablename)
    sql = Block[Any](raw("DELETE FROM"), tablename)
    if where is not None:
        sql += Block(raw("WHERE"), where)
    if return_fields is not None:
        sql += Block(raw("RETURNING"), join(raw(","), *return_fields))
    return wrap(sql)


def update(
    table: Model | Type[Model] | Block[Any],
    values: dict[SQL[Any], SQL[Any]],
    where: Block[Bool] | None = None,
    return_fields: Sequence[BaseField[Any, Any, Any] | Block[Any]]
    | None = None,
) -> Block[Any]:
    tablename = table if isinstance(table, Block) else raw(table.tablename)
    sql = Block[Any](raw("UPDATE"), tablename, raw("SET"))

    set_logic: list[Block[Any]] = []
    for key, value in values.items():
        set_logic.append(Block(key, raw("="), value))

    sql += join(raw(","), *set_logic)

    if where is not None:
        sql += Block(raw("WHERE"), where)

    if return_fields is not None:
        sql += Block(raw("RETURNING"), join(raw(","), *return_fields))

    return wrap(sql)


def insert(
    into: Model | Type[Model] | Block[Any],
    fields: Sequence[BaseField[Any, Any, Any] | Block[Any]],
    values: Sequence[SQL[Any]],
    return_fields: Sequence[BaseField[Any, Any, Any] | Block[Any]]
    | None = None,
) -> Block[Any]:
    tablename = into if isinstance(into, Block) else raw(into.tablename)

    sql = Block[Any](raw("INSERT INTO"), tablename)
    if len(fields) > 0:
        sql += join(raw(","), *fields, wrap=True)

    if len(values) > 0:
        sql += Block[Any](raw("VALUES"), join(raw(","), *values, wrap=True))
    else:
        sql += Block[Any](raw("DEFAULT VALUES"))

    if return_fields is not None:
        sql += raw("RETURNING")
        if isinstance(return_fields, (BaseField, Block)):
            sql += return_fields
        else:
            sql += join(raw(","), *return_fields)

    return wrap(sql)

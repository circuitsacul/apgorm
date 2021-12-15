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

from typing import TYPE_CHECKING, Any, Sequence, Type, TypeVar

from apgorm.field import Field
from apgorm.sql.sql import SQL, Block
from apgorm.types.base_type import SqlType
from apgorm.types.boolean import Bool

from .helpers import join, r, wrap

if TYPE_CHECKING:
    from apgorm.model import Model


_SQLT = TypeVar("_SQLT", bound=SqlType)


# TODO: any difference between :: and CAST AS?
def cast(param: SQL, type_: Type[_SQLT]) -> Block[_SQLT]:
    return Block(param, r("::"), r(type_.sql_name), wrap=True)


def select(
    from_: Model | Type[Model] | Block,
    fields: Sequence[Field | Block] | None = None,
    where: Block[Bool] | None = None,
    order_by: Field | Block | None = None,
    ascending: bool = True,
) -> Block[Any]:
    sql = Block[Any](r("SELECT"))

    if fields is None:
        sql += Block(r("*"))
    else:
        sql += join(r(","), *fields, wrap=True)

    tablename = from_ if isinstance(from_, Block) else r(from_.tablename)
    sql += Block(r("FROM"), tablename)

    if where is not None:
        sql += Block(r("WHERE "), where)

    if order_by is not None:
        sql += Block(r("ORDER BY"), order_by)
        sql += r("ASC" if ascending else "DESC")

    return wrap(sql)


def delete(
    from_: Model | Type[Model] | Block,
    where: Block[Bool] | None = None,
) -> Block:
    tablename = from_ if isinstance(from_, Block) else r(from_.tablename)
    sql = Block[Any](r("DELETE FROM"), tablename)
    if where is not None:
        sql += Block(r("WHERE"), where)
    return wrap(sql)


def update(
    table: Model | Type[Model] | Block,
    values: dict[SQL, SQL],
    where: Block[Bool] | None = None,
) -> Block:
    tablename = table if isinstance(table, Block) else r(table.tablename)
    sql = Block[Any](r("UPDATE"), tablename, r("SET"))

    set_logic: list[Block] = []
    for key, value in values.items():
        set_logic.append(Block(key, r("="), value))

    sql += join(r(","), *set_logic)

    if where is not None:
        sql += Block(r("WHERE"), where)

    return wrap(sql)


def insert(
    into: Model | Type[Model] | Block,
    fields: Sequence[Field | Block],
    values: Sequence[SQL],
    return_fields: Sequence[Field | Block] | Field | Block | None = None,
) -> Block[Any]:
    tablename = into if isinstance(into, Block) else r(into.tablename)

    sql = Block[Any](r("INSERT INTO"), tablename)
    if len(fields) > 0:
        sql += join(r(","), *fields, wrap=True)

    if len(values) > 0:
        sql += Block[Any](r("VALUES"), join(r(","), *values, wrap=True))
    else:
        sql += Block[Any](r("DEFAULT VALUES"))

    if return_fields is not None:
        sql += r("RETURNING")
        if isinstance(return_fields, (Field, Block)):
            sql += return_fields
        else:
            sql += join(r(","), *return_fields, wrap=True)

    return wrap(sql)

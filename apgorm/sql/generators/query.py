from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence, Type, TypeVar

from apgorm.field import Field
from apgorm.sql.sql import SQL, Sql
from apgorm.types.base_type import SqlType

from .helpers import join, parenthesis, r

if TYPE_CHECKING:
    from apgorm.model import Model


_T = TypeVar("_T")


@parenthesis  # TODO: any difference between :: and CAST AS?
def cast(param: SQL, type_: Type[SqlType[_T]]) -> Sql[_T]:
    return Sql(param, r("::"), r(type_.sql_name))


@parenthesis
def select(
    from_: Model | Type[Model] | Sql,
    fields: Sequence[Field | Sql] | None = None,
    where: Sql[bool] | None = None,
    order_by: Field | Sql | None = None,
    ascending: bool = True,
) -> Sql[Any]:
    sql = Sql[Any](r("SELECT"))

    if fields is None:
        sql += Sql(r("*"))
    else:
        sql += Sql(r("("), join(r(","), *fields), r(")"))

    tablename = from_ if isinstance(from_, Sql) else r(from_.tablename)
    sql += Sql(r("FROM"), tablename)

    if where is not None:
        sql += Sql(r("WHERE "), where)

    if order_by is not None:
        sql += Sql(r("ORDER BY"), order_by)
        sql += r("ASC" if ascending else "DESC")

    return sql


@parenthesis
def delete(
    from_: Model | Type[Model] | Sql,
    where: Sql[bool] | None = None,
) -> Sql[None]:
    tablename = from_ if isinstance(from_, Sql) else r(from_.tablename)
    sql = Sql[None](r("DELETE FROM"), tablename)
    if where is not None:
        sql += Sql(r("WHERE"), where)
    return sql


@parenthesis
def update(
    table: Model | Type[Model] | Sql,
    values: dict[SQL, SQL],
    where: Sql[bool] | None = None,
) -> Sql[None]:
    tablename = table if isinstance(table, Sql) else r(table.tablename)
    sql = Sql[None](r("UPDATE"), tablename, r("SET"))

    set_logic: list[Sql] = []
    for key, value in values.items():
        set_logic.append(Sql(key, r("="), value))

    sql += join(r(","), *set_logic)

    if where is not None:
        sql += Sql(r("WHERE"), where)

    return sql


@parenthesis
def insert(
    into: Model | Type[Model] | Sql,
    fields: Sequence[Field | Sql],
    values: Sequence[SQL],
    return_fields: Sequence[Field | Sql] | Field | Sql | None = None,
) -> Sql[Any]:
    tablename = into if isinstance(into, Sql) else r(into.tablename)
    sql = Sql[Any](
        r("INSERT INTO"),
        tablename,
        r("("),
        join(r(","), *fields),
        r(")"),
        r("VALUES"),
        r("("),
        join(r(","), *values),
        r(")"),
    )
    if return_fields is not None:
        sql += r("RETURNING")
        if isinstance(return_fields, (Field, Sql)):
            sql += return_fields
        else:
            sql += Sql(r("("), join(r(","), *return_fields), r(")"))

    return sql

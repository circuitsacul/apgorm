from __future__ import annotations

from apgorm.sql.sql import SQL, Sql

from .helpers import join, parenthesis, r


@parenthesis
def or_(*values: SQL[bool]) -> Sql[bool]:
    return join(r("OR"), *values)


@parenthesis
def and_(*values: SQL[bool]) -> Sql[bool]:
    return join(r("AND"), *values)


@parenthesis
def not_(value: SQL[bool]) -> Sql[bool]:
    return Sql(r("NOT"), value)


@parenthesis
def between(value: SQL, low: SQL, high: SQL) -> Sql[bool]:
    return Sql(value, "BETWEEN", low, "AND", high)


@parenthesis
def not_between(value: SQL, low: SQL, high: SQL) -> Sql[bool]:
    return Sql(value, "NOT BETWEEN", low, "AND", high)


@parenthesis
def between_symmetric(value: SQL, first: SQL, second: SQL) -> Sql[bool]:
    return Sql(value, "BETWEEN SYMMETRIC", first, "AND", second)


@parenthesis
def not_between_symmetric(value: SQL, first: SQL, second: SQL) -> Sql[bool]:
    return Sql(value, "NOT BETWEEN SYMMETRIC", first, "AND", second)


@parenthesis
def is_distinct(value: SQL, from_: SQL) -> Sql[bool]:
    return Sql(value, "IS DISTINCT FROM", from_)


@parenthesis
def is_not_distinct(value: SQL, from_: SQL) -> Sql[bool]:
    return Sql(value, "IS NOT DISTINCT FROM", from_)


@parenthesis
def is_null(value: SQL) -> Sql[bool]:
    return Sql(value, "IS NULL")


@parenthesis
def is_not_null(value: SQL) -> Sql[bool]:
    return Sql(value, "IS NOT NUlL")


@parenthesis
def is_true(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS TRUE")


@parenthesis
def is_not_true(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS NOT TRUE")


@parenthesis
def is_false(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS FALSE")


@parenthesis
def is_not_false(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS NOT FALSE")


@parenthesis
def is_unkown(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS UNKOWN")


@parenthesis
def is_not_unkown(value: SQL[bool | None]) -> Sql[bool]:
    return Sql(value, "IS NOT UNKOWN")


@parenthesis
def eq(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r("="), right)


@parenthesis
def neq(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r("!="), right)


@parenthesis
def lt(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r("<"), right)


@parenthesis
def gt(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r(">"), right)


@parenthesis
def lteq(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r("<="), right)


@parenthesis
def gteq(left: SQL, right: SQL) -> Sql[bool]:
    return Sql[bool](left, r(">="), right)

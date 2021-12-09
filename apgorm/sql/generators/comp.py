from __future__ import annotations

from apgorm.sql.sql import SQL, Block
from apgorm.types.boolean import Bool

from .helpers import join, r


def or_(*values: SQL[bool]) -> Block[Bool]:
    return join(r("OR"), *values, wrap=True)


def and_(*values: SQL[bool]) -> Block[Bool]:
    return join(r("AND"), *values, wrap=True)


def not_(value: SQL[bool]) -> Block[Bool]:
    return Block(r("NOT"), value, wrap=True)


def between(value: SQL, low: SQL, high: SQL) -> Block[Bool]:
    return Block(value, "BETWEEN", low, "AND", high, wrap=True)


def not_between(value: SQL, low: SQL, high: SQL) -> Block[Bool]:
    return Block(value, "NOT BETWEEN", low, "AND", high, wrap=True)


def between_symmetric(value: SQL, first: SQL, second: SQL) -> Block[Bool]:
    return Block(value, "BETWEEN SYMMETRIC", first, "AND", second, wrap=True)


def not_between_symmetric(value: SQL, first: SQL, second: SQL) -> Block[Bool]:
    return Block(
        value, "NOT BETWEEN SYMMETRIC", first, "AND", second, wrap=True
    )


def is_distinct(value: SQL, from_: SQL) -> Block[Bool]:
    return Block(value, "IS DISTINCT FROM", from_, wrap=True)


def is_not_distinct(value: SQL, from_: SQL) -> Block[Bool]:
    return Block(value, "IS NOT DISTINCT FROM", from_, wrap=True)


def is_null(value: SQL) -> Block[Bool]:
    return Block(value, "IS NULL", wrap=True)


def is_not_null(value: SQL) -> Block[Bool]:
    return Block(value, "IS NOT NUlL", wrap=True)


def is_true(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS TRUE", wrap=True)


def is_not_true(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS NOT TRUE", wrap=True)


def is_false(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS FALSE", wrap=True)


def is_not_false(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS NOT FALSE", wrap=True)


def is_unkown(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS UNKOWN", wrap=True)


def is_not_unkown(value: SQL[bool | None]) -> Block[Bool]:
    return Block(value, "IS NOT UNKOWN", wrap=True)


def eq(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r("="), right, wrap=True)


def neq(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r("!="), right, wrap=True)


def lt(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r("<"), right, wrap=True)


def gt(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r(">"), right, wrap=True)


def lteq(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r("<="), right, wrap=True)


def gteq(left: SQL, right: SQL) -> Block[Bool]:
    return Block(left, r(">="), right, wrap=True)

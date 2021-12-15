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

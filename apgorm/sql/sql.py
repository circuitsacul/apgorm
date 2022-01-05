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

from collections import UserString
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

if TYPE_CHECKING:
    from apgorm.field import BaseField
    from apgorm.types.base_type import SqlType
    from apgorm.types.boolean import Bool

_T = TypeVar("_T", covariant=True)
_SQLT = TypeVar("_SQLT", bound="SqlType", covariant=True)
_PARAM = TypeVar("_PARAM")
SQL = Union[
    "BaseField[SqlType[_T], _T, Any]",
    "Block[SqlType[_T]]",
    "Parameter[_T]",
    _T,
]
CASTED = Union[
    "BaseField[_SQLT, Any, Any]",
    "Block[_SQLT]",
]


def wrap(*pieces: SQL) -> Block:
    return Block(*pieces, wrap=True)


def join(joiner: SQL, *values: SQL, wrap: bool = False) -> Block:
    new_values: list[SQL] = []
    for x, v in enumerate(values):
        new_values.append(v)
        if x != len(values) - 1:
            new_values.append(joiner)
    return Block(*new_values, wrap=wrap)


def r(string: str) -> Block:
    return Block(Raw(string))


def p(param: _PARAM) -> Parameter[_PARAM]:
    return Parameter(param)


class Raw(UserString):
    pass


class Parameter(Generic[_T]):
    def __init__(self, value: _T):
        self.value = value


class Comparable:
    def _get_block(self) -> Block:
        raise NotImplementedError

    def _op(self, op: str, other: SQL) -> Block[Bool]:
        return wrap(self._get_block(), r(op), other)

    def _opjoin(self, op: str, *values: SQL) -> Block[Bool]:
        return join(r(op), self._get_block(), *values)

    def _func(self, func: str) -> Block:
        return wrap(func, wrap(self._get_block()))

    def _rfunc(self, rfunc: str) -> Block:
        return wrap(wrap(self._get_block()), rfunc)

    def or_(self, *values: SQL[bool]) -> Block[Bool]:
        return self._opjoin("OR", *values)

    def and_(self, *values: SQL[bool]) -> Block[Bool]:
        return self._opjoin("AND", *values)

    def not_(self) -> Block[Bool]:
        return self._func("NOT")

    def between(self, low: SQL, high: SQL) -> Block[Bool]:
        return wrap(self._get_block(), r("BETWEEN"), low, r("AND"), high)

    def not_between(self, low: SQL, high: SQL) -> Block[Bool]:
        return wrap(self._get_block(), r("NOT BETWEEN"), low, r("AND"), high)

    def between_symmetric(self, first: SQL, second: SQL) -> Block[Bool]:
        return wrap(
            self._get_block(),
            r("BETWEEN SYMMETRIC"),
            first,
            r("AND"),
            second,
        )

    def not_between_symmetric(self, first: SQL, second: SQL) -> Block[Bool]:
        return wrap(
            self._get_block(),
            r("NOT BETWEEN SYMMETRIC"),
            first,
            r("AND"),
            second,
        )

    def is_distinct(self, from_: SQL) -> Block[Bool]:
        return self._op("IS DISTINCT", from_)

    def is_not_distinct(self, from_: SQL) -> Block[Bool]:
        return self._op("IS NOT DISTINCT", from_)

    def is_null(self) -> Block[Bool]:
        return self._rfunc("IS NULL")

    def is_not_null(self) -> Block[Bool]:
        return self._rfunc("IS NOT NULL")

    def is_true(self) -> Block[Bool]:
        return self._rfunc("IS TRUE")

    def is_not_true(self) -> Block[Bool]:
        return self._rfunc("IS NOT TRUE")

    def is_false(self) -> Block[Bool]:
        return self._rfunc("IS FALSE")

    def is_not_false(self) -> Block[Bool]:
        return self._rfunc("IS NOT FALSE")

    def is_unkown(self) -> Block[Bool]:
        return self._rfunc("IS UNKOWN")

    def is_not_unkown(self) -> Block[Bool]:
        return self._rfunc("IS NOT UNKOWN")

    def eq(self, other: SQL) -> Block[Bool]:
        return self._op("=", other)

    def neq(self, other: SQL) -> Block[Bool]:
        return self._op("!=", other)

    def lt(self, other: SQL) -> Block[Bool]:
        return self._op("<", other)

    def gt(self, other: SQL) -> Block[Bool]:
        return self._op(">", other)

    def lteq(self, other: SQL) -> Block[Bool]:
        return self._op("<=", other)

    def gteq(self, other: SQL) -> Block[Bool]:
        return self._op(">=", other)


class Block(Comparable, Generic[_SQLT]):
    def __init__(self, *pieces: SQL | Raw, wrap: bool = False):
        self._pieces: list[Raw | Parameter] = []

        if len(pieces) == 1 and isinstance(pieces[0], Block):
            block = pieces[0]
            assert isinstance(block, Block)
            self.wrap: bool = block.wrap or wrap
            self._pieces = block._pieces

        else:
            self.wrap = wrap
            for p in pieces:
                if isinstance(p, Comparable):
                    p = p._get_block()
                if isinstance(p, Block):
                    self._pieces.extend(p.get_pieces())
                elif isinstance(p, (Raw, Parameter)):
                    self._pieces.append(p)
                else:
                    self._pieces.append(Parameter(p))

    def _get_block(self) -> Block:
        return self

    def render(self) -> tuple[str, list[Any]]:
        return Renderer().render(self)

    def render_no_params(self) -> str:
        return self.render()[0]

    def get_pieces(
        self, force_wrap: bool | None = None
    ) -> list[Raw | Parameter]:
        wrap = self.wrap if force_wrap is None else force_wrap
        if wrap:
            return [Raw("("), *self._pieces, Raw(")")]
        return self._pieces

    def __iadd__(self, other: object):
        if isinstance(other, Block):
            self._pieces.extend(other.get_pieces())
        elif isinstance(other, Parameter):
            self._pieces.append(other)
        else:
            raise TypeError(f"Unsupported type {type(other)}")

        return self


class Renderer:
    def __init__(self):
        self._curr_value_id: int = 0

    @property
    def next_value_id(self) -> int:
        self._curr_value_id += 1
        return self._curr_value_id

    def render(self, sql: Block) -> tuple[str, list[Any]]:
        sql_pieces: list[str] = []
        params: list[Any] = []

        for piece in sql.get_pieces(force_wrap=False):
            if isinstance(piece, Raw):
                sql_pieces.append(str(piece))
            else:
                sql_pieces.append(f"${self.next_value_id}")
                params.append(piece.value)

        return " ".join(sql_pieces), params

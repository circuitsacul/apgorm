from __future__ import annotations

from typing import TypeVar, Union

from apgorm.sql.sql import SQL, Block, Parameter, Raw

_T = TypeVar("_T")
NUM = Union[float, int]


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


def p(param: _T) -> Parameter[_T]:
    return Parameter(param)

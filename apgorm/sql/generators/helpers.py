from __future__ import annotations

from typing import Callable, TypeVar, Union

from apgorm.sql.sql import SQL, Block, Parameter, Raw

_F = TypeVar("_F", bound=Callable[..., Block])
_T = TypeVar("_T")
NUM = Union[float, int]


def parenthesis(function: _F) -> _F:
    def wrapper(*args, **kwargs) -> Block:
        sql = function(*args, **kwargs)
        return Block(r("("), sql, r(")"))

    return wrapper  # type: ignore


def join(joiner: SQL, *values: SQL) -> Block:
    new_values: list[SQL] = []
    for x, v in enumerate(values):
        new_values.append(v)
        if x != len(values) - 1:
            new_values.append(joiner)
    return Block(*new_values)


def r(string: str) -> Block:
    return Block(Raw(string))


def p(param: _T) -> Parameter[_T]:
    return Parameter(param)

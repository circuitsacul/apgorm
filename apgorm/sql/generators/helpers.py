from __future__ import annotations

from typing import Callable, TypeVar, Union

from apgorm.sql.sql import SQL, Parameter, Raw, Sql

_F = TypeVar("_F", bound=Callable[..., Sql])
_T = TypeVar("_T")
NUM = Union[float, int]


def parenthesis(function: _F) -> _F:
    def wrapper(*args, **kwargs) -> Sql:
        sql = function(*args, **kwargs)
        return Sql(r("("), sql, r(")"))

    return wrapper  # type: ignore


def join(joiner: SQL, *values: SQL) -> Sql:
    new_values: list[SQL] = []
    for x, v in enumerate(values):
        new_values.append(v)
        if x != len(values) - 1:
            new_values.append(joiner)
    return Sql(*new_values)


def r(string: str) -> Sql:
    return Sql(Raw(string))


def p(param: _T) -> Parameter[_T]:
    return Parameter(param)

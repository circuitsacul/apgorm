from __future__ import annotations

from collections import UserString
from typing import TYPE_CHECKING, Any, Generic, TypeVar, Union

from apgorm.field import Field

if TYPE_CHECKING:
    from apgorm.types.base_type import SqlType

_T = TypeVar("_T", covariant=True)
_SQLT = TypeVar("_SQLT", bound="SqlType", covariant=True)
SQL = Union[
    "Field[SqlType[_T], _T]",
    "Block[SqlType[_T]]",
    "Parameter[_T]",
    _T,
]
CASTED = Union[
    "Field[_SQLT, Any]",
    "Block[_SQLT]",
]


class Raw(UserString):
    pass


class Parameter(Generic[_T]):
    def __init__(self, value: _T):
        self.value = value


class Block(Generic[_SQLT]):
    def __init__(self, *pieces: SQL | Raw):
        self.pieces: list[Raw | Parameter] = []
        for p in pieces:
            if isinstance(p, Field):
                self.pieces.append(Raw(p.full_name))
            elif isinstance(p, Block):
                self.pieces.extend(p.pieces)
            elif isinstance(p, (Raw, Parameter)):
                self.pieces.append(p)
            else:
                self.pieces.append(Parameter(p))

    def __iadd__(self, other: object):
        if isinstance(other, Block):
            self.pieces.extend(other.pieces)
        elif isinstance(other, Parameter):
            self.pieces.append(other)
        elif isinstance(other, Field):
            self.pieces.append(Raw(other.full_name))
        else:
            raise TypeError

        return self

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

from apgorm.field import BaseField

if TYPE_CHECKING:
    from apgorm.types.base_type import SqlType

_T = TypeVar("_T", covariant=True)
_SQLT = TypeVar("_SQLT", bound="SqlType", covariant=True)
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


class Raw(UserString):
    pass


class Parameter(Generic[_T]):
    def __init__(self, value: _T):
        self.value = value


class Block(Generic[_SQLT]):
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
                if isinstance(p, BaseField):
                    self._pieces.append(Raw(p.name))
                elif isinstance(p, Block):
                    self._pieces.extend(p.get_pieces())
                elif isinstance(p, (Raw, Parameter)):
                    self._pieces.append(p)
                else:
                    self._pieces.append(Parameter(p))

    def render(self) -> tuple[str, list[Any]]:
        return Renderer().render(self)

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
        elif isinstance(other, BaseField):
            self._pieces.append(Raw(other.full_name))
        else:
            raise TypeError

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

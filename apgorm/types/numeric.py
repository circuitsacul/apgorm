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

from decimal import Decimal
from typing import TypeVar, Union

from apgorm.exceptions import BadArgument
from apgorm.field import Field

from .base_type import SqlType

INT = Union["SmallInt", "Int", "BigInt"]
FLOAT = Union["Real", "DoublePrecision", "Numeric"]
SERIAL = Union["SmallSerial", "Serial", "BigSerial"]

NUMBER = Union[INT, FLOAT, SERIAL]


class SmallInt(SqlType[int]):
    sql = "SMALLINT"


class Int(SqlType[int]):
    sql = "INTEGER"


Integer = Int


class BigInt(SqlType[int]):
    sql = "BIGINT"


class Numeric(SqlType[Decimal]):
    def __init__(
        self,
        precision: int | None = None,
        scale: int | None = None,
    ):
        self._precision = precision
        self._scale = scale

        self.sql = "NUMERIC"

        if precision is not None and scale is not None:
            self.sql += f"({precision}, {scale})"
        elif precision is not None:
            self.sql += f"({precision})"
        elif scale is not None:
            raise BadArgument("Cannot specify scale without precision.")


class Real(SqlType[float]):
    sql = "REAL"


class DoublePrecision(SqlType[float]):
    sql = "DOUBLE PRECISION"


_S = TypeVar("_S", bound="_BaseSerial", covariant=True)


class _BaseSerial(SqlType[int]):
    def field(  # type: ignore
        self: _S,
        pk: bool = False,
        unique: bool = False,
        read_only: bool = False,
    ) -> Field[_S, int]:
        return Field(
            sql_type=self,
            not_null=True,
            pk=pk,
            unique=unique,
            read_only=read_only,
        )

    def nullablefield(  # type: ignore
        self: _S,
        pk: bool = False,
        unique: bool = False,
        read_only: bool = False,
    ) -> Field[_S, int | None]:
        return Field(
            sql_type=self,
            not_null=False,
            pk=pk,
            unique=unique,
            read_only=read_only,
        )


class SmallSerial(_BaseSerial):
    sql = "SMALLSERIAL"


class Serial(_BaseSerial):
    sql = "SERIAL"


class BigSerial(_BaseSerial):
    sql = "BIGSERIAL"

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

import datetime
from decimal import Decimal

import asyncpg
from asyncpg import BitString

import apgorm
from apgorm.types import (  # json; monetary; network; uuid_type; xml
    array,
    binary,
    bitstr,
    boolean,
    character,
    date,
    geometric,
    numeric,
)


class PrimaryModel(apgorm.Model):
    # arrays
    ul_array = array.Array(numeric.Int()).field(default=[])
    ul_null_array = array.Array(numeric.Int()).nullablefield()
    array_2d = array.Array(array.Array(numeric.Int())).field()

    # binary
    bytea = binary.ByteA().field(default=b"hello, world")

    # bitstr
    bit5 = bitstr.Bit(5).field(default=BitString(b"hello"))
    bit1 = bitstr.Bit().field(default=BitString(b"h"))
    varbit5 = bitstr.VarBit(5).field(default=BitString(b"hi"))
    varbit_ul = bitstr.VarBit().field(default=BitString(b"hello, world"))

    # bool
    bool_field = boolean.Boolean().field(default=True)

    # char
    varchar_ul = character.VarChar().field(default="hello, world")
    varchar_5 = character.VarChar(5).field(default="hi")
    char_1 = character.Char().field(default="h")
    char_5 = character.Char().field(default="hi")  # should pad with spaces

    # date  # NOTE: we don't test precision here
    timestamp = date.Timestamp().field(default=datetime.datetime.now(tz=None))
    timestamptz = date.TimestampTZ().field(
        default=datetime.datetime.now(tz=datetime.timezone.utc)
    )
    time = date.Time().field(default=datetime.time(tzinfo=None))
    timetz = date.TimeTZ().field(
        default=datetime.time(tzinfo=datetime.timezone.utc)
    )

    # geometric
    point = geometric.Point().field(default=asyncpg.Point(0, 0))
    line = geometric.Line().field(default=asyncpg.Line(0, 1, 0))
    lineseg = geometric.LineSegment().field(
        default=asyncpg.LineSegment((0, 0), (1, 0))
    )
    box = geometric.Box().field(default=asyncpg.Box((0, 0), (5, 5)))

    # integer types
    serial = numeric.Serial().field()
    smallserial = numeric.SmallSerial().field()
    bigserial = numeric.BigSerial().field()

    smallint = numeric.SmallInt().field()
    integer = numeric.Int().field()
    bigint = numeric.BigInt().field()

    real = numeric.Real().field(default=1.0)
    double_precision = numeric.DoublePrecision().field(default=1.0)
    decimal_norm = numeric.Numeric().field(default=Decimal())
    decimal_6p = numeric.Numeric(6).field(default=Decimal())
    decimal_6p_2s = numeric.Numeric(6, 2).field(default=Decimal())

    primary_key = (
        serial,
        smallserial,
        bigserial,
    )


class Referenced(apgorm.Model):
    serial = numeric.Serial().field()

    primary_key = (serial,)


class Database(apgorm.Database):
    primary = PrimaryModel
    referenced = Referenced

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
import uuid
from decimal import Decimal
from ipaddress import IPv4Address, IPv4Network

import asyncpg
from asyncpg import BitString

import apgorm
from apgorm.constraints import ForeignKey
from apgorm.indexes import Index, IndexType
from apgorm.types import (
    array,
    binary,
    bitstr,
    boolean,
    character,
    date,
    geometric,
    json_type,
    monetary,
    network,
    numeric,
    uuid_type,
    xml_type,
)
from apgorm.utils import LazyList


class PrimaryModel(apgorm.Model):
    # arrays
    ul_array = array.Array(numeric.Int()).field(default=[])
    ul_null_array = array.Array(numeric.Int()).nullablefield()
    array_2d = array.Array(array.Array(numeric.Int())).field()

    # binary
    bytea = binary.ByteA().field(default=b"hello, world")

    # bitstr
    bit5 = bitstr.Bit(5).field(default=BitString.frombytes(b"01001"))
    bit1 = bitstr.Bit().field(default=BitString.frombytes(b"1"))
    varbit5 = bitstr.VarBit(5).field(default=BitString.frombytes(b"10"))
    varbit_ul = bitstr.VarBit().field(
        default=BitString.frombytes(b"100001111")
    )

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

    # json type
    json = json_type.Json().field(default="{}")
    jsonb = json_type.JsonB().field(default="{}")

    # money types
    money = monetary.Money().field(default="$5")

    # network types
    cidr = network.CIDR().field(default=IPv4Network("192.0.2.0/27"))
    inet = network.INET().field(default=IPv4Address("192.0.2.0"))
    macaddr = network.MacAddr().field(default="08:00:2b:01:02:03")
    macaddr8 = network.MacAddr8().field(default="08:00:2b:01:02:03:04:05")

    # number types
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

    # uuid
    guid = uuid_type.UUID().field(
        default=uuid.UUID("{12345678-1234-5678-1234-567812345678}")
    )

    # xml
    xml = xml_type.XML().field(default="<foo>bar</foo>")

    # primary key
    primary_key = (
        serial,
        smallserial,
        bigserial,
    )


class Indexed(apgorm.Model):
    pk = numeric.Serial().field()

    ibtree = numeric.Int().field(default=1)
    ihash = numeric.Int().field(default=1)

    igist = geometric.Point().field(default=asyncpg.Point(1, 1))
    ispgist = geometric.Point().field(default=asyncpg.Point(1, 1))

    igin = array.Array(numeric.Int()).field(default=[1, 2, 3])
    ibrin = numeric.Int().field(default=1)

    primary_key = (pk,)


class User(apgorm.Model):
    name = character.VarChar(32).field()
    nickname = character.VarChar(32).nullablefield()

    primary_key = (name,)

    async def games(self) -> LazyList[dict, Game]:
        return (
            await Game.fetch_query()
            .where(
                Player.fetch_query()
                .where(
                    username=self.name.v,
                    gameid=Game.gameid,
                )
                .exists()
            )
            .fetchmany()
        )

    async def players(self) -> LazyList[dict, Player]:
        return (
            await Player.fetch_query().where(username=self.name.v).fetchmany()
        )


class Game(apgorm.Model):
    gameid = numeric.Serial().field()

    primary_key = (gameid,)

    async def players(self) -> LazyList[dict, Player]:
        return (
            await Player.fetch_query().where(gameid=self.gameid.v).fetchmany()
        )

    async def users(self) -> LazyList[dict, User]:
        return (
            await User.fetch_query()
            .where(
                Player.fetch_query()
                .where(username=User.name, gameid=self.gameid.v)
                .exists()
            )
            .fetchmany()
        )


class Player(apgorm.Model):
    username = character.VarChar(32).field()
    gameid = numeric.Int().field()

    username_fk = ForeignKey(username, User.name)
    gameid_fk = ForeignKey(gameid, Game.gameid)

    primary_key = (
        username,
        gameid,
    )


class Database(apgorm.Database):
    primary_table = PrimaryModel
    indexed_table = Indexed
    users = User
    games = Game
    players = Player

    indexes = [
        Index(Indexed, Indexed.ibtree, IndexType.BTREE),
        Index(Indexed, Indexed.ihash, IndexType.HASH),
        Index(Indexed, Indexed.igist, IndexType.GIST),
        Index(Indexed, Indexed.ispgist, IndexType.SPGIST),
        Index(Indexed, Indexed.igin, IndexType.GIN),
        Index(Indexed, Indexed.ibrin, IndexType.BRIN),
    ]

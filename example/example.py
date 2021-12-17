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

from enum import IntEnum, IntFlag

from apgorm import Converter, Model
from apgorm.constraints import ForeignKey
from apgorm.types.character import VarChar
from apgorm.types.numeric import Int, Serial


class UserFlags(IntFlag):
    PRO_USER = 1 << 0
    BANNED = 1 << 1


class PlayerStatus(IntEnum):
    NOT_FINISHED = 0
    WINNER = 1
    LOSER = 2
    DROPPED = 3


class UserFlagsConverter(Converter[int, UserFlags]):
    def to_stored(self, value: UserFlags) -> int:
        return int(value)

    def from_stored(self, value: int) -> UserFlags:
        return UserFlags(value)


class PlayerStatusConverter(Converter[int, PlayerStatus]):
    def to_stored(self, value: PlayerStatus) -> int:
        return int(value)

    def from_stored(self, value: int) -> PlayerStatus:
        return PlayerStatus(value)


class User(Model):
    tablename = "users"

    username = VarChar(32).field(unique=True)
    nickname = VarChar(32).nullablefield(default=None)
    user_flags = Int().field(default=0).with_converter(UserFlagsConverter)


class Game(Model):
    tablename = "games"

    name = VarChar(32).field()


class Player(Model):
    tablename = "players"

    user_id = Serial().field()
    game_id = Serial().field()
    status = Int().field(default=0).with_converter(PlayerStatusConverter)

    user_id_fk = ForeignKey([user_id], [User.id_])
    game_id_fk = ForeignKey([game_id], [Game.id_])

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

from enum import IntEnum
from pathlib import Path

import apgorm
from apgorm.types import Int, VarChar


class PlayerStatus(IntEnum):
    NOT_FINISHED = 0
    WINNER = 1
    LOSER = 2
    DROPPED = 3


class PlayerStatusConverter(apgorm.Converter[int, PlayerStatus]):
    def to_stored(self, value: PlayerStatus) -> int:
        return int(value)

    def from_stored(self, value: int) -> PlayerStatus:
        return PlayerStatus(value)


class Player(apgorm.Model):
    username = VarChar(32).field()
    status = Int().field(default=0).with_converter(PlayerStatusConverter)

    primary_key = (username,)


class Database(apgorm.Database):
    players = Player


async def _main():
    player = await Player(
        username="Circuit", status=PlayerStatus.NOT_FINISHED
    ).create()
    print("Created player", player)

    print("player.status.v:", player.status.v)  # PlayerStatus.NOT_FINISHED
    print("players.status._value:", player.status._value)  # 0

    player.status.v = PlayerStatus.WINNER
    await player.save()
    print(f"Set status to {player.status.v!r} ({player.status._value!r})")

    await player.delete()


async def main():
    db = Database(Path("examples/converters/migrations"))
    await db.connect(database="apgorm_testing_database")

    if db.must_create_migrations():
        db.create_migrations()
    if await db.must_apply_migrations():
        await db.apply_migrations()

    try:
        await _main()
    finally:
        await db.cleanup()

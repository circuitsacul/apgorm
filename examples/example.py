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

import asyncio
import random
from enum import IntEnum

import apgorm
from apgorm.constraints import ForeignKey
from apgorm.sql.generators.comp import neq
from apgorm.types.character import VarChar
from apgorm.types.numeric import Int, Serial


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


class User(apgorm.Model):
    id_ = Serial().field(pk=True, read_only=True, use_eq=True)
    username = VarChar(32).field(unique=True)
    nickname = VarChar(32).nullablefield(default=None)


class Game(apgorm.Model):
    id_ = Serial().field(pk=True, read_only=True, use_eq=True)
    name = VarChar(32).field()


class Player(apgorm.Model):
    id_ = Serial().field(pk=True, read_only=True, use_eq=True)
    user_id = Int().field()
    game_id = Int().field()
    status = Int().field(default=0).with_converter(PlayerStatusConverter)

    user_id_fk = ForeignKey([user_id], [User.id_])
    game_id_fk = ForeignKey([game_id], [Game.id_])


class Database(apgorm.Database):
    users = User
    games = Game
    players = Player


async def _main(db: Database):
    # delete stuff to ensure we don't violate any unique constraints
    await User.delete_query().execute()
    await Game.delete_query().execute()
    # technically this is unecessary because ON DELETE is set to cascade
    await Player.delete_query().execute()

    # create some users:
    usernames = ["Circuit", "James", "Unamed"]
    for un in usernames:
        await User(username=un).create()

    # create some games:
    game_names = ["Game 1", "Game 2"]
    for gn in game_names:
        await Game(name=gn).create()

    # get all users except the one named "Unamed"
    all_users = (
        await User.fetch_query()
        .where(neq(User.username, "Unamed"))
        .fetchmany()
    )

    # get all games
    all_games = await Game.fetch_query().fetchmany()

    # add some players (or, attach some users to games)
    for user in all_users:
        for game in all_games:
            await Player(user_id=user.id_.v, game_id=game.id_.v).create()

    # print the players
    print(await Player.fetch_query().fetchmany())

    # set a random winner for each game
    for game in all_games:
        players = (
            await Player.fetch_query().where(game_id=game.id_.v).fetchmany()
        )

        winner = random.choice(players)
        winner.status.v = PlayerStatus.WINNER
        await winner.save()


async def main():
    db = Database()
    await db.connect(database="apgorm")
    try:
        await _main(db)
    finally:
        await db.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

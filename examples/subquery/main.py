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

import random
from pathlib import Path

import apgorm
from apgorm.constraints import ForeignKey
from apgorm.types import Int, Serial, VarChar


class User(apgorm.Model):
    name = VarChar(32).field()

    primary_key = (name,)


class Game(apgorm.Model):
    id_ = Serial().field()

    primary_key = (id_,)


class Player(apgorm.Model):
    username = VarChar(32).field()
    gameid = Int().field()

    username_fk = ForeignKey(username, User.name)
    gameid_fk = ForeignKey(gameid, Game.id_)

    primary_key = (
        username,
        gameid,
    )


class Database(apgorm.Database):
    users = User
    games = Game
    players = Player


async def _main(db: Database):
    # migrations
    if db.must_create_migrations():
        db.create_migrations()
    if await db.must_apply_migrations():
        await db.apply_migrations()

    # delete stuff (don't want to run into unique violations)
    await User.delete_query().execute()
    await Game.delete_query().execute()

    # create some stuff
    usernames = ["Circuit", "User 2", "James", "Superman", "Batman"]
    for un in usernames:
        await User(name=un).create()

    for _ in range(0, 5):
        await Game().create()

    all_users = await User.fetch_query().fetchmany()
    all_games = await Game.fetch_query().fetchmany()

    # add users to games randomly
    for g in all_games:
        for u in all_users:
            if random.randint(0, 1) == 1:
                await Player(gameid=g.id_.v, username=u.name.v).create()

    # for each user, get all their games (using subqueries)
    for user in all_users:
        print(f"Games {user} is in:")

        _games = (
            await Game.fetch_query()
            .where(
                Player.fetch_query()
                .where(gameid=Game.id_, username=user.name.v)
                .exists()
            )
            .fetchmany()
        )

        print(" - " + "\n - ".join([repr(g) for g in _games]))


async def main():
    db = Database(Path("examples/subquery/migrations"))
    await db.connect(database="apgorm")
    try:
        await _main(db)
    finally:
        await db.cleanup()

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

from apgorm.sql.generators.comp import neq

from .database import Database, Game, Player, PlayerStatus, User


def _check_migration_status(db: Database):
    if db.must_create_migrations():
        print("Warning: Migrations need creating!")
        db.create_migrations()
    else:
        print("Migrations up-to-date!")


async def _main(db: Database):
    print("\nDelete stuff to ensure we don't violate any unique constraints:")
    await User.delete_query().execute()
    await Game.delete_query().execute()
    print(
        "Technically this is unecessary because ON DELETE is set to cascade:"
    )
    await Player.delete_query().execute()

    print("\nCreate some users:")
    usernames = ["Circuit", "James", "Unamed"]
    for un in usernames:
        await User(username=un).create()

    print("\nCreate some games:")
    game_names = ["Game 1", "Game 2"]
    for gn in game_names:
        await Game(name=gn).create()

    print('\nGet all users except the one named "Unamed":')
    all_users = (
        await User.fetch_query()
        .where(neq(User.username, "Unamed"))
        .fetchmany()
    )

    print("\nGet all games:")
    all_games = await Game.fetch_query().fetchmany()

    print("\nAdd some players (or, attach some users to games)")
    for user in all_users:
        for game in all_games:
            await Player(user_id=user.id_.v, game_id=game.id_.v).create()

    print("\nPrint the players, users, and games:")
    print("\n".join([repr(p) for p in await Player.fetch_query().fetchmany()]))
    print("\n".join([repr(g) for g in await Game.fetch_query().fetchmany()]))
    print("\n".join([repr(u) for u in await User.fetch_query().fetchmany()]))

    print("\nSet a random winner for each game:")
    for game in all_games:
        players = (
            await Player.fetch_query().where(game_id=game.id_.v).fetchmany()
        )

        winner = random.choice(players)
        winner.status.v = PlayerStatus.WINNER
        await winner.save()


async def main():
    migrations_folder = Path("examples/advanced/migrations")
    db = Database(migrations_folder)
    await db.connect(database="apgorm")
    try:
        _check_migration_status(db)
        await _main(db)
    finally:
        await db.cleanup()

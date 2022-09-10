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


async def _main() -> None:
    player = await Player(
        username="Circuit", status=PlayerStatus.NOT_FINISHED
    ).create()
    print("Created player", player)

    print("player.status:", player.status)  # PlayerStatus.NOT_FINISHED
    print("players.status raw value:", player._raw_values["status"])  # 0

    player.status = PlayerStatus.WINNER
    await player.save()
    print(f"Set status to {player.status!r}")

    await player.delete()


async def main() -> None:
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

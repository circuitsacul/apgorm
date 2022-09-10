from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path
from typing import Iterable

from .describe import Describe


class Migration:
    """Represents a single migrations."""

    __slots__: Iterable[str] = ("describe", "migrations", "path")

    def __init__(
        self, describe: Describe, migrations: str, path: Path
    ) -> None:
        self.describe = describe
        """The Database.describe() at the time this migration was created."""
        self.migrations = migrations
        """The raw SQL used for applying the migration."""
        self.path = path
        """The path at which the migration can be found."""

    @property
    def migration_id(self) -> int:
        """The id of the migration.

        Returns:
            int: The migration id.
        """

        return self._id_from_path(self.path)

    @classmethod
    def _from_path(cls, path: Path) -> Migration:
        with (path / "describe.json").open("r") as f:
            describe = Describe(**json.loads(f.read()))

        with (path / "migrations.sql").open("r") as f:
            sql = f.read()

        return cls(describe, sql, path)

    @staticmethod
    def _path_from_id(migration_id: int, folder: Path, padding: int) -> Path:
        return folder / str(migration_id).zfill(padding)

    @staticmethod
    def _id_from_path(path: Path) -> int:
        return int(path.name)

    @classmethod
    def _load_all_migrations(cls, folder: Path) -> list[Migration]:
        migrations: list[Migration] = []
        for p in folder.glob("*"):
            if p.is_file():
                continue

            with suppress(FileNotFoundError):
                migrations.append(cls._from_path(p))

        return migrations

    @classmethod
    def _load_last_migration(cls, folder: Path) -> Migration | None:
        migrations = cls._load_all_migrations(folder)
        if not migrations:
            return None
        migrations.sort(key=lambda m: m.migration_id)
        return migrations[-1]

    @classmethod
    def _create_migration(
        cls,
        describe: Describe,
        migrations: str,
        folder: Path,
        padding: int = 0,
    ) -> Migration:
        last_migration = cls._load_last_migration(folder)
        if last_migration:
            next_id = last_migration.migration_id + 1
        else:
            next_id = 0
        next_path = folder / str(next_id).zfill(padding)
        next_path.mkdir(parents=True, exist_ok=False)
        with (next_path / "describe.json").open("w+") as f:
            f.write(json.dumps(describe.dict(), indent=4))
        with (next_path / "migrations.sql").open("w+") as f:
            f.write(migrations)

        return cls(describe, migrations, next_path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Migration):
            raise TypeError(f"Unsupported type {type(other)}")
        return self.migration_id == other.migration_id

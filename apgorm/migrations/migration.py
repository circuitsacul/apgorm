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

import json
from pathlib import Path
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from apgorm import Database


class Migration:
    def __init__(self, path: Path):
        self.path = path
        self._raw_data: dict | None = None

    def raw_data(self, cache: bool = True) -> dict:
        if cache and self._raw_data:
            return self._raw_data

        with open(self.path, "r") as f:
            res = json.loads(f.read())

        assert isinstance(res, dict)
        self._raw_data = res
        return res

    def describe(self) -> dict:
        desc = self.raw_data()["describe"]
        assert isinstance(desc, dict)
        return desc

    @property
    def migration_id(self) -> int:
        return int(self.path.name.strip(".json"))

    @staticmethod
    def filename_from_id(migration_id: int) -> str:
        return f"{migration_id}.json"

    @classmethod
    def load_all_migrations(
        cls: Type[Migration], folder: Path
    ) -> list[Migration]:
        return [cls(path) for path in folder.glob("*json")]

    @classmethod
    def load_last_migration(
        cls: Type[Migration], folder: Path
    ) -> Migration | None:
        paths = [cls(p) for p in folder.glob("*.json")]
        if len(paths) == 0:
            return None
        paths.sort(key=lambda m: m.migration_id)
        return paths[0]

    @classmethod
    def must_create_migrations(cls: Type[Migration], db: Database) -> bool:
        last_migration = cls.load_last_migration(db.migrations_folder)
        if last_migration is None:
            return True

        return last_migration.describe() != db.describe()

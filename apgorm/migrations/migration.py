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
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Type

if TYPE_CHECKING:
    from apgorm import Database


@dataclass
class TableRename:
    original_name: str
    new_name: str


@dataclass
class FieldAddDrop:
    table: str
    name: str


@dataclass
class FieldRename:
    table: str
    original_name: str
    new_name: str


@dataclass
class FieldConstraintAddDrop:
    table: str
    field: str
    constraint: str


@dataclass
class TableConstraintAdd:
    table: str
    name: str
    raw_sql: str
    params: list[Any]


@dataclass
class TableConstraintDrop:
    table: str
    name: str


@dataclass
class Migration:
    path: str

    describe: dict

    new_tables: list[str]
    dropped_tables: list[str]
    renamed_tables: list[TableRename]

    new_table_constraints: list[TableConstraintAdd]
    dropped_table_constraints: list[TableConstraintDrop]

    new_fields: list[FieldAddDrop]
    dropped_fields: list[FieldAddDrop]
    renamed_fields: list[FieldRename]

    new_field_constraints: list[FieldConstraintAddDrop]
    dropped_field_constraints: list[FieldConstraintAddDrop]

    @property
    def migration_id(self) -> int:
        return int(Path(self.path).name.strip(".json"))

    @staticmethod
    def filename_from_id(migration_id: int) -> str:
        return f"{migration_id}.json"

    @classmethod
    def from_path(cls: Type[Migration], path: Path) -> Migration:
        with open(path, "r") as f:
            data = json.loads(f.read())

        return cls(path=str(path), **data)

    @classmethod
    def load_all_migrations(
        cls: Type[Migration], folder: Path
    ) -> list[Migration]:
        return [cls.from_path(path) for path in folder.glob("*json")]

    @classmethod
    def load_last_migration(
        cls: Type[Migration], folder: Path
    ) -> Migration | None:
        all_migrations = cls.load_all_migrations(folder)
        if len(all_migrations) == 0:
            return None
        all_migrations.sort(key=lambda m: m.migration_id)
        return all_migrations[0]

    @classmethod
    def must_create_migrations(cls: Type[Migration], db: Database) -> bool:
        last_migration = cls.load_last_migration(db.migrations_folder)
        if last_migration is None:
            return True

        return last_migration.describe != db.describe()

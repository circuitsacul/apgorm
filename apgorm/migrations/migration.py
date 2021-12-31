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
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Type, Union

import asyncpg

from apgorm.migrations.describe import Describe, DescribeTable
from apgorm.undefined import UNDEF
from apgorm.utils import nested_dataclass

if TYPE_CHECKING:
    from apgorm import Database


def _dict_factory(result: list[tuple[Any, Any]]) -> dict:
    result = [r for r in result if r[1] is not UNDEF.UNDEF]
    return dict(result)


@nested_dataclass
class TableRename:
    original_name: str
    new_name: str


@nested_dataclass
class FieldAdd:
    table: str
    name: str
    type_: str
    default: Union[Any, UNDEF] = UNDEF.UNDEF


@nested_dataclass
class FieldDrop:
    table: str
    name: str


@nested_dataclass
class FieldRename:
    table: str
    original_name: str
    new_name: str


@nested_dataclass
class ConstraintAdd:
    table: str
    name: str
    raw_sql: str
    params: List[Any]


@nested_dataclass
class ConstraintDrop:
    table: str
    name: str


@nested_dataclass
class Migration:
    path: str

    describe: Describe

    new_tables: List[str]
    dropped_tables: List[str]
    renamed_tables: List[TableRename]

    new_constraints: List[ConstraintAdd]
    dropped_constraints: List[ConstraintDrop]

    new_fields: List[FieldAdd]
    dropped_fields: List[FieldDrop]
    renamed_fields: List[FieldRename]

    def save(self, indent: int | None = None):
        with open(self.path, "w+") as f:
            f.write(json.dumps(self.todict(), indent=indent))

    def todict(self):
        d = asdict(self, dict_factory=_dict_factory)
        del d["path"]
        return d

    def isempty(self) -> bool:
        must_be_empty = [
            "new_tables",
            "dropped_tables",
            "renamed_tables",
            "new_constraints",
            "dropped_constraints",
            "new_fields",
            "dropped_fields",
            "renamed_fields",
        ]
        for attr in must_be_empty:
            v = getattr(self, attr)
            if isinstance(v, list) and len(v) > 0:
                return False

        return True

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
        return all_migrations[-1]

    @classmethod
    def must_create_migrations(cls: Type[Migration], db: Database) -> bool:
        return not cls.create_migrations(db).isempty()

    @classmethod
    def create_migrations(cls: Type[Migration], db: Database) -> Migration:
        return _create_next_migration(cls, db)

    @classmethod
    async def load_unapplied_migrations(
        cls: Type[Migration], db: Database
    ) -> list[Migration]:
        all_migrations = cls.load_all_migrations(db.migrations_folder)
        by_id = {m.migration_id: m for m in all_migrations}
        try:
            async for applied_migration in (
                db._migrations.fetch_query().cursor()
            ):
                del by_id[applied_migration.id_.v]
        except asyncpg.exceptions.UndefinedTableError:
            pass

        return list(by_id.values())


def _create_next_migration(
    cls: Type[Migration],
    db: Database,
) -> Migration:  # TODO: handle renaming stuff
    lm = cls.load_last_migration(db.migrations_folder)
    cd = db.describe()

    curr_tables_dict = {t.name: t for t in cd.tables}
    last_tables_dict = {t.name: t for t in lm.describe.tables} if lm else {}

    # tables TODO: renamed tables
    new_tables = [
        key for key in curr_tables_dict if key not in last_tables_dict
    ]
    dropped_tables = [
        key for key in last_tables_dict if key not in curr_tables_dict
    ]

    # table constraints, fields, and field constraints
    new_constraints: list[ConstraintAdd] = []
    dropped_constraints: list[ConstraintDrop] = []

    new_fields: list[FieldAdd] = []
    dropped_fields: list[FieldDrop] = []

    for tablename, currtable in curr_tables_dict.items():
        lasttable: DescribeTable | None = None
        if tablename in last_tables_dict:
            lasttable = last_tables_dict[tablename]

        # table constraints
        curr_constraints = {c.name: c for c in currtable.constraints}
        if lasttable:
            last_constraints = {c.name: c for c in lasttable.constraints}
        else:
            last_constraints = {}

        new_constraints.extend(
            [
                ConstraintAdd(tablename, key, c.raw_sql, c.params)
                for key, c in curr_constraints.items()
                if key not in last_constraints
            ]
        )
        dropped_constraints.extend(
            [
                ConstraintDrop(tablename, key)
                for key in last_constraints
                if key not in curr_constraints
            ]
        )

        for constraint in curr_constraints.values():
            last_constraint = last_constraints.get(constraint.name, None)
            if not last_constraint:
                continue

            if (
                constraint.raw_sql == last_constraint.raw_sql
                and constraint.params == last_constraint.params
            ):
                continue

            dropped_constraints.append(
                ConstraintDrop(tablename, constraint.name)
            )
            new_constraints.append(
                ConstraintAdd(
                    tablename,
                    constraint.name,
                    constraint.raw_sql,
                    constraint.params,
                )
            )

        # fields
        curr_fields = {f.name: f for f in currtable.fields}
        if lasttable:
            last_fields = {f.name: f for f in lasttable.fields}
        else:
            last_fields = {}

        new_fields.extend(
            [
                FieldAdd(tablename, key, f.type_, f.default)
                for key, f in curr_fields.items()
                if key not in last_fields
            ]
        )
        dropped_fields.extend(
            [
                FieldDrop(tablename, key)
                for key in last_fields
                if key not in curr_fields
            ]
        )

    # finalization
    next_id = lm.migration_id + 1 if lm else 0
    new_path = str(db.migrations_folder / cls.filename_from_id(next_id))
    return cls(
        path=new_path,
        describe=cd,
        new_tables=new_tables,
        dropped_tables=dropped_tables,
        renamed_tables=[],
        new_constraints=new_constraints,
        dropped_constraints=dropped_constraints,
        new_fields=new_fields,
        dropped_fields=dropped_fields,
        renamed_fields=[],
    )

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

from typing import TYPE_CHECKING

from apgorm.undefined import UNDEF

if TYPE_CHECKING:
    from apgorm.sql.sql import SQL, Block


class TypeDesc:
    def __init__(self, creation_sql: Block):
        self.creation_sql = creation_sql

    def __repr__(self) -> str:
        return self.creation_sql.render()[0]


class FieldDesc:
    def __init__(
        self,
        name: str,
        default: SQL | UNDEF,
        not_null: bool,
        type_desc: TypeDesc,
    ):
        self.name = name
        self.default = default
        self.not_null = not_null
        self.type_desc = type_desc

    def __repr__(self) -> str:
        return (
            f"Field {self.name} "
            + repr(self.type_desc)
            + (
                f" DEFAULT {self.default} "
                if self.default is not UNDEF.UNDEF
                else " "
            )
            + ("NOT NULL " if self.not_null else "")
        )


class ConstraintDesc:
    def __init__(self, creation_sql: Block):
        self.creation_sql = creation_sql

    def __repr__(self) -> str:
        return self.creation_sql.render()[0]


class ModelDesc:
    def __init__(
        self,
        name: str,
        fields: dict[str, FieldDesc],
        constraints: dict[str, ConstraintDesc],
    ):
        self.name = name
        self.fields = fields
        self.constraints = constraints

    def __repr__(self) -> str:
        return (
            f"Model {self.name}"
            + "\n\tFields\n\t\t{}".format(
                "\n\t\t".join([repr(f) for f in self.fields.values()])
            )
            + "\n\tConstraints\n\t\t{}".format(
                "\n\t\t".join([repr(c) for c in self.constraints.values()])
            )
        )


class DatabaseDesc:
    def __init__(
        self,
        models: dict[str, ModelDesc],
    ):
        self.models = models

    def __repr__(self) -> str:
        return "\n\n".join([repr(m) for m in self.models.values()])

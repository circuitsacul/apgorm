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

from enum import Enum
from typing import List, Sequence
from typing import cast as typingcast

from apgorm.exceptions import BadArgument
from apgorm.field import BaseField
from apgorm.sql.generators.helpers import join, r
from apgorm.sql.sql import Block

from .constraint import Constraint


class Action(Enum):
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class ForeignKey(Constraint):
    def __init__(
        self,
        fields: Sequence[Block | BaseField],
        ref_fields: Sequence[Block | BaseField],
        ref_table: Block | None = None,
        match_full: bool = False,
        on_delete: Action = Action.CASCADE,
        on_update: Action = Action.CASCADE,
    ):
        self.fields = fields
        self.ref_fields = ref_fields
        self.ref_table = ref_table
        self.match_full = match_full
        self.on_delete = on_delete
        self.on_update = on_update

        if len(ref_fields) != len(fields):
            raise BadArgument(
                "Must have same number of fields and ref_fields."
            )

        if len(fields) == 0:
            raise BadArgument("Must specify at least on field and ref_field.")

    def creation_sql(self) -> Block:
        ref_table: Block
        ref_fields: list[Block] = []

        if (
            len(
                {
                    f.model.tablename
                    for f in self.ref_fields
                    if isinstance(f, BaseField)
                }
            )
            > 1
        ):
            raise BadArgument(
                "All fields in ref_fields must be of the same table."
            )

        if self.ref_table is None:
            _ref_fields = self.ref_fields
            if not all([isinstance(f, BaseField) for f in _ref_fields]):
                raise BadArgument(
                    "ref_fields must either all be BaseFields or "
                    "ref_table must be specified."
                )
            _ref_fields = typingcast(List[BaseField], _ref_fields)

            ref_table = r(_ref_fields[0].model.tablename)

        else:
            ref_table = self.ref_table

        ref_fields = [
            r(f.name) if isinstance(f, BaseField) else f
            for f in self.ref_fields
        ]
        fields = [
            r(f.name) if isinstance(f, BaseField) else f for f in self.fields
        ]

        return Block(
            r("CONSTRAINT"),
            r(self.name),
            r("FOREIGN KEY ("),
            join(r(","), *fields),
            r(") REFERENCES"),
            ref_table,
            r("("),
            join(r(","), *ref_fields),
            r(f") ON DELETE {self.on_delete.value}"),
            r(f"ON UPDATE {self.on_update.value}"),
            wrap=True,
        )

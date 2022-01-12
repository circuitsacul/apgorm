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
from typing import Sequence
from typing import cast as typingcast

from apgorm.exceptions import BadArgument
from apgorm.field import BaseField
from apgorm.sql.sql import Block, join, r

from .constraint import Constraint


class ForeignKeyAction(Enum):
    """Action for ON UPDATE or ON DELETE of ForeignKey."""

    CASCADE = "CASCADE"
    """Carry the changes"""
    RESTRICT = "RESTRICT"
    """Prevent the changes"""
    NO_ACTION = "NO ACTION"
    """Do nothing"""


class ForeignKey(Constraint):
    def __init__(
        self,
        fields: Sequence[Block | BaseField | str] | Block | BaseField | str,
        ref_fields: Sequence[Block | BaseField | str]
        | Block
        | BaseField
        | str,
        ref_table: Block | str | None = None,
        match_full: bool = False,
        on_delete: ForeignKeyAction = ForeignKeyAction.CASCADE,
        on_update: ForeignKeyAction = ForeignKeyAction.CASCADE,
    ) -> None:
        """Specify a ForeignKey constraint for a table.

        Args:
            fields (Sequence[Block | BaseField]): A list of fields or raw
            field names on the current table.
            ref_fields (Sequence[Block | BaseField]): A list of fields or raw
            field names on the referenced table.
            ref_table (Block, optional): If all of `ref_fields` are `Block`,
            specify the raw tablename of the referenced table. Defaults to
            None.
            match_full (bool, optional): Whether or not a full match is
            required. If False, MATCH SIMPLE is used instead. Defaults to
            False.
            on_delete (Action, optional): The action to perform if the
            referenced row is deleted. Defaults to Action.CASCADE.
            on_update (Action, optional): The action to perform if the
            referenced row is updated. Defaults to Action.CASCADE.

        Raises:
            BadArgument: Bad arguments were sent to ForeignKey.
        """

        self.fields: Sequence[BaseField | Block] = [
            r(f) if isinstance(f, str) else f
            for f in (fields if isinstance(fields, Sequence) else [fields])
        ]
        self.ref_fields: Sequence[BaseField | Block] = [
            r(f) if isinstance(f, str) else f
            for f in (
                ref_fields
                if isinstance(ref_fields, Sequence)
                else [ref_fields]
            )
        ]
        self.ref_table = (
            r(ref_table) if isinstance(ref_table, str) else ref_table
        )
        self.match_full = match_full
        self.on_delete = on_delete
        self.on_update = on_update

        if len(self.ref_fields) != len(self.fields):
            raise BadArgument(
                "Must have same number of fields and ref_fields."
            )

        if len(self.fields) == 0:
            raise BadArgument("Must specify at least on field and ref_field.")

    def _creation_sql(self) -> Block:
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
            _ref_fields = typingcast(Sequence[BaseField], _ref_fields)

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
            (r(") MATCH FULL") if self.match_full else r(") MATCH SIMPLE")),
            r(f"ON DELETE {self.on_delete.value}"),
            r(f"ON UPDATE {self.on_update.value}"),
            wrap=True,
        )

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

from typing import TYPE_CHECKING, Any

from apgorm.indexes import IndexType, _IndexType
from apgorm.sql.sql import Block, join, r, wrap

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.field import BaseField
    from apgorm.types.boolean import Bool


class Exclude(Constraint):
    def __init__(
        self,
        *elements: tuple[BaseField | Block | str, str],
        using: IndexType = IndexType.BTREE,
        where: Block[Bool] | str | None = None
    ) -> None:
        """Specify an Exclusion constraint for a table.

        Args:
            *elements: key-value pairs of fields and the operator to use on
            that field.

        Kwargs:
            using (IndexType, optional): The index to use. Defaults
            to IndexType.BTREE.
            where (Block[Bool] | str, optional): Specify condition for
            applying this constraint. Defaults to None.
        """

        self.using: _IndexType = using.value
        self.elements = [
            (r(f) if isinstance(f, str) else f, op) for f, op in elements
        ]
        self.where = r(where) if isinstance(where, str) else where

    def _creation_sql(self) -> Block:
        sql = Block[Any](
            r("CONSTRAINT"),
            r(self.name),
            r("EXCLUDE USING"),
            r(self.using.name),
            join(
                r(","),
                *[wrap(f, r("WITH"), r(op)) for f, op in self.elements],
                wrap=True,
            ),
        )
        if self.where is not None:
            sql += Block(r("WHERE"), wrap(self.where))

        return sql

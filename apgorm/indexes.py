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

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Sequence, Type

from apgorm.exceptions import BadArgument
from apgorm.field import BaseField
from apgorm.migrations.describe import DescribeIndex
from apgorm.sql.sql import Block, join, r, wrap

if TYPE_CHECKING:
    from apgorm.model import Model


@dataclass
class _IndexType:
    name: str
    multi: bool = False
    unique: bool = False


class IndexType(Enum):
    BTREE = _IndexType("BTREE", multi=True, unique=True)
    HASH = _IndexType("HASH")
    GIST = _IndexType("GIST", multi=True)
    SP_GIST = _IndexType("SPGIST")
    GIN = _IndexType("GIN", multi=True)
    BRIN = _IndexType("BRIN", multi=True)


class Index:
    def __init__(
        self,
        table: Type[Model],
        fields: Sequence[BaseField | Block] | BaseField | Block,
        type_: IndexType = IndexType.BTREE,
        unique: bool = False,
    ):
        self.type_: _IndexType = type_.value
        if isinstance(fields, (Block, BaseField)):
            fields = [fields]
        self.fields = fields
        self.table = table
        self.unique = unique

        if len(fields) == 0:
            raise BadArgument("Must specify at least one field for index.")

        if (not self.type_.multi) and len(fields) > 1:
            raise BadArgument(f"{type_.name} indexes only support one column.")

        if (not self.type_.unique) and unique:
            raise BadArgument(
                f"{type_.name} indexes do not support uniqueness."
            )

    def get_name(self) -> str:
        fields = [f.name for f in self.fields if isinstance(f, BaseField)]
        return "_{type_}_index_{table}__{cols}".format(
            type_=self.type_.name,
            table=self.table._tablename,
            cols="_".join(fields),
        ).lower()

    def creation_sql(self) -> Block:
        return Block(
            (r("UNIQUE INDEX") if self.unique else r("INDEX")),
            r(self.get_name()),
            r("ON"),
            r(self.table._tablename),
            r("USING"),
            r(self.type_.name),
            r("("),
            join(r(","), *[wrap(f) for f in self.fields]),
            r(")"),
        )

    def describe(self) -> DescribeIndex:
        return DescribeIndex(
            name=self.get_name(),
            raw_sql=self.creation_sql().render_no_params(),
        )

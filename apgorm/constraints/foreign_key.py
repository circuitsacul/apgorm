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
from typing import TYPE_CHECKING, Sequence

from apgorm.sql.generators.helpers import join, r
from apgorm.sql.sql import Block

from .constraint import Constraint

if TYPE_CHECKING:
    from apgorm.field import BaseField


class Action(Enum):
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class ForeignKey(Constraint):
    def __init__(
        self,
        fields: Sequence[BaseField],
        ref_fields: Sequence[BaseField],
        match_full: bool = False,
        on_delete: Action = Action.CASCADE,
        on_update: Action = Action.CASCADE,
    ):
        self.fields = fields
        self.ref_fields = ref_fields
        self.match_full = match_full
        self.on_delete = on_delete
        self.on_update = on_update

    def creation_sql(self) -> Block:
        return Block(
            r("CONSTRAINT"),
            r(self.name),
            r("FOREIGN KEY ("),
            join(r(","), self.fields),
            r(") REFERENCES ("),
            join(r(","), self.ref_fields),
            wrap=True,
        )

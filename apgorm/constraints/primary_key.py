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

from apgorm.sql.sql import Block, join, r

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.field import BaseField


class PrimaryKey(Constraint):
    def __init__(self, *fields: BaseField | Block | str) -> None:
        """Do not use. Specify primary keys like this instead:

        ```
        class Users(Model):
            username = VarChar(32).field()

            primary_key = (username,)
        ```
        """

        self.fields = [
            r(f)
            if isinstance(f, str)
            else f
            if isinstance(f, Block)
            else r(f.name)
            for f in fields
        ]

    def _creation_sql(self) -> Block:
        return Block(
            r("CONSTRAINT"),
            r(self.name),
            r("PRIMARY KEY ("),
            join(r(","), *self.fields),
            r(")"),
            wrap=True,
        )

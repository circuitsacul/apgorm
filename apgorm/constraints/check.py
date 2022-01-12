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

from apgorm.sql.sql import Block, r

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.types.boolean import Bool


class Check(Constraint):
    def __init__(self, check: Block[Bool] | str) -> None:
        """Specify a check constraint for a table.

        Args:
            check (Block[Bool]): The raw SQL for the check constraint.
        """

        self.check = r(check) if isinstance(check, str) else check

    def _creation_sql(self) -> Block:
        return Block(
            r("CONSTRAINT"),
            r(self.name),
            r("CHECK"),
            Block(self.check, wrap=True),
            wrap=True,
        )

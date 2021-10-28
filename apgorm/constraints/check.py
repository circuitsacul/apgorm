from __future__ import annotations

from typing import TYPE_CHECKING

from .constraint import Constraint

if TYPE_CHECKING:
    from apgorm.sql.sql import Block


class Check(Constraint):
    def __init__(self, check: Block[bool]):
        self.check = check

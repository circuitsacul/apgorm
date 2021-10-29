from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from .constraint import Constraint

if TYPE_CHECKING:
    from apgorm.field import Field
    from apgorm.sql import Block


class PrimaryKey(Constraint):
    def __init__(self, fields: Sequence[Field | Block]):
        self.fields = fields

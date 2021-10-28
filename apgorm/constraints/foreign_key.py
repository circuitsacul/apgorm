from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Sequence

from apgorm.sql.sql import Block

from .constraint import Constraint

if TYPE_CHECKING:
    from apgorm.fields import Field


class Action(Enum):
    CASCADE = "CASCADE"
    RESTRICT = "RESTRICT"
    NO_ACTION = "NO ACTION"


class ForeignKey(Constraint):
    def __init__(
        self,
        fields: Sequence[Field | Block],
        ref_fields: Sequence[Field | Block],
        match_full: bool = False,
        on_delete: Action = Action.CASCADE,
        on_update: Action = Action.CASCADE,
    ):
        self.fields = fields
        self.ref_fields = ref_fields
        self.match_full = match_full
        self.on_delete = on_delete
        self.on_update = on_update

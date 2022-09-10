from __future__ import annotations

from typing import Iterable

from apgorm.model import Model
from apgorm.types.numeric import Int


class AppliedMigration(Model):
    __slots__: Iterable[str] = ()

    id_ = Int().field()

    primary_key = (id_,)

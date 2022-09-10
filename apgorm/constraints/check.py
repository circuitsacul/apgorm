from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from apgorm.sql.sql import Block, raw

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.types.boolean import Bool


class Check(Constraint):
    __slots__: Iterable[str] = ("check",)

    def __init__(self, check: Block[Bool] | str) -> None:
        """Specify a check constraint for a table.

        Args:
            check (Block[Bool]): The raw SQL for the check constraint.
        """

        self.check = raw(check) if isinstance(check, str) else check

    def _creation_sql(self) -> Block[Any]:
        return Block(
            raw("CONSTRAINT"),
            raw(self.name),
            raw("CHECK"),
            Block(self.check, wrap=True),
            wrap=True,
        )

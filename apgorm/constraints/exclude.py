from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from apgorm.indexes import IndexType, _IndexType
from apgorm.sql.sql import Block, join, raw, wrap

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.field import BaseField
    from apgorm.types.boolean import Bool


class Exclude(Constraint):
    __slots__: Iterable[str] = ("using", "elements", "where")

    def __init__(
        self,
        *elements: tuple[BaseField[Any, Any, Any] | Block[Any] | str, str],
        using: IndexType = IndexType.BTREE,
        where: Block[Bool] | str | None = None,
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
            (raw(f) if isinstance(f, str) else f, op) for f, op in elements
        ]
        self.where = raw(where) if isinstance(where, str) else where

    def _creation_sql(self) -> Block[Any]:
        sql = Block[Any](
            raw("CONSTRAINT"),
            raw(self.name),
            raw("EXCLUDE USING"),
            raw(self.using.name),
            join(
                raw(","),
                *(wrap(f, raw("WITH"), raw(op)) for f, op in self.elements),
                wrap=True,
            ),
        )
        if self.where is not None:
            sql += Block(raw("WHERE"), wrap(self.where))

        return sql

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterable

from apgorm.sql.sql import Block, join, raw

from .constraint import Constraint

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.field import BaseField


class Unique(Constraint):
    __slots__: Iterable[str] = ("fields",)

    def __init__(
        self, *fields: BaseField[Any, Any, Any] | Block[Any] | str
    ) -> None:
        """Specify a unique constraint for a table.

        ```
        class User(Model):
            ...
            nickname = VarChar(32).field()
            nickname_unique = Unique(nickname)
            ...
        ```
        """

        self.fields = fields

    def _creation_sql(self) -> Block[Any]:
        fields = (
            raw(f)
            if isinstance(f, str)
            else f
            if isinstance(f, Block)
            else raw(f.name)
            for f in self.fields
        )
        return Block(
            raw("CONSTRAINT"),
            raw(self.name),
            raw("UNIQUE ("),
            join(raw(","), *fields),
            raw(")"),
            wrap=True,
        )

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Iterable, Sequence, Type

from .exceptions import BadArgument
from .field import BaseField
from .migrations.describe import DescribeIndex
from .sql.sql import Block, join, raw, wrap

if TYPE_CHECKING:  # pragma: no cover
    from .model import Model


@dataclass
class _IndexType:
    name: str
    multi: bool = False
    unique: bool = False


class IndexType(Enum):
    """An enum containing every supported index type."""

    BTREE = _IndexType("BTREE", multi=True, unique=True)
    HASH = _IndexType("HASH")
    GIST = _IndexType("GIST", multi=True)
    SPGIST = _IndexType("SPGIST")
    GIN = _IndexType("GIN", multi=True)
    BRIN = _IndexType("BRIN", multi=True)


class Index:
    """Represents an index for a table.

    Must be added to Database.indexes before the database is initialized. For
    example:
    ```
    class MyDatabase(Database):
        ...

        indexes = [Index(...), Index(...), ...]
    ```

    Args:
        table (Type[Model]): The table this index is for.
        fields (Sequence[BaseField): A list of fields that this index is for.
        type_ (IndexType, optional): The index type. Defaults to
        IndexType.BTREE.
        unique (bool, optional): Whether or not the index should be unique
        (BTREE only). Defaults to False.

    Raises:
        BadArgument: Bad arguments were passed to Index.
    """

    __slots__: Iterable[str] = ("type_", "fields", "table", "unique")

    def __init__(
        self,
        table: Type[Model],
        fields: Sequence[BaseField[Any, Any, Any] | Block[Any] | str]
        | BaseField[Any, Any, Any]
        | Block[Any]
        | str,
        type_: IndexType = IndexType.BTREE,
        unique: bool = False,
    ) -> None:
        self.type_: _IndexType = type_.value
        if not isinstance(fields, Sequence):
            fields = [fields]
        self.fields = [raw(f) if isinstance(f, str) else f for f in fields]
        self.table = table
        self.unique = unique

        if not fields:
            raise BadArgument("Must specify at least one field for index.")

        if (not self.type_.multi) and len(fields) > 1:
            raise BadArgument(f"{type_.name} indexes only support one column.")

        if (not self.type_.unique) and unique:
            raise BadArgument(
                f"{type_.name} indexes do not support uniqueness."
            )

    def get_name(self) -> str:
        """Create a name based on the type, table, and fields of the index.

        Returns:
            str: The name.
        """

        fields = (f.name for f in self.fields if isinstance(f, BaseField))
        return "_{type_}_index_{table}__{cols}".format(
            type_=self.type_.name,
            table=self.table.tablename,
            cols="_".join(fields),
        ).lower()

    def _creation_sql(self) -> Block[Any]:
        names = (
            wrap(f) if isinstance(f, Block) else wrap(raw(f.name))
            for f in self.fields
        )

        return Block(
            (raw("UNIQUE INDEX") if self.unique else raw("INDEX")),
            raw(self.get_name()),
            raw("ON"),
            raw(self.table.tablename),
            raw("USING"),
            raw(self.type_.name),
            raw("("),
            join(raw(","), *names),
            raw(")"),
        )

    def _describe(self) -> DescribeIndex:
        return DescribeIndex(
            name=self.get_name(),
            raw_sql=self._creation_sql().render_no_params(),
        )

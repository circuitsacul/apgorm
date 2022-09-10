from __future__ import annotations

from typing import Iterable

from .base_type import SqlType


class Boolean(SqlType[bool]):
    """Boolean type.

    Note: Although the docs say that "null" is valid as a bool value, `col
    bool not null` still refuses null values.

    https://www.postgresql.org/docs/14/datatype-boolean.html
    """

    __slots__: Iterable[str] = ()

    _sql = "BOOLEAN"


Bool = Boolean

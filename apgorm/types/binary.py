from __future__ import annotations

from typing import Iterable

from .base_type import SqlType


class ByteA(SqlType[bytes]):
    """Variable-length binary string.

    https://www.postgresql.org/docs/14/datatype-binary.html
    """

    __slots__: Iterable[str] = ()

    _sql = "BYTEA"

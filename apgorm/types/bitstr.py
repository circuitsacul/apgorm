from __future__ import annotations

from typing import Iterable

import asyncpg

from .base_type import SqlType


class Bit(SqlType[asyncpg.BitString]):
    """Fixed length string of 0's and 1's.

    Args:
        length (int, optional): The length of the bitstr. If None,
        postgres uses 1. Defaults to None.

    https://www.postgresql.org/docs/14/datatype-bit.html
    """

    __slots__: Iterable[str] = ("_length",)

    def __init__(self, length: int | None = None) -> None:
        self._length = length
        self._sql = "BIT"
        if length is not None:
            self._sql += f"({length})"

    @property
    def length(self) -> int | None:
        """The length of the bitstr.

        Returns:
            int | None
        """

        return self._length


class VarBit(SqlType[asyncpg.BitString]):
    """Variable-length bitstr with max-length.

    https://www.postgresql.org/docs/14/datatype-bit.html
    """

    def __init__(self, max_length: int | None = None) -> None:
        """Create a VarBit type.

        Args:
            max_length (int, optional): The maximum bitstr length. If None the
            length is unlimited. Defaults to None.
        """

        self._max_length = max_length
        self._sql = "VARBIT"
        if max_length is not None:
            self._sql += f"({max_length})"

    @property
    def max_length(self) -> int | None:
        """The maximum length of the bitstr.

        Returns:
            int | None
        """

        return self._max_length

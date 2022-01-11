# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import asyncpg

from .base_type import SqlType


class Bit(SqlType[asyncpg.BitString]):
    """Fixed length string of 0's and 1's.

    Args:
        length (int, optional): The length of the bitstr. If None,
        postgres uses 1. Defaults to None.

    https://www.postgresql.org/docs/14/datatype-bit.html
    """

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

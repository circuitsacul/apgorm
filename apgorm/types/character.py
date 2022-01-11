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

from .base_type import SqlType


class VarChar(SqlType[str]):
    """Variable length string with limit.

    Args:
        max_length (int, optional): The maximum length of the string. If
        None, any length will be accepted. Defaults to None.

    https://www.postgresql.org/docs/14/datatype-character.html
    """

    def __init__(self, max_length: int | None = None) -> None:
        self._max_length = max_length
        self._sql = "VARCHAR"
        if max_length is not None:
            self._sql += f"({max_length})"

    @property
    def max_length(self) -> int | None:
        """The maximum length of the VarChar type.

        Returns:
            int | None
        """

        return self._max_length


class Char(SqlType[str]):
    """Fixed length string. If a passed string is too short, it will be
    padded with spaces.

    Args:
        max_length (int, optional): The length of the string. If None,
        postgres will use 1. Defaults to None.

    https://www.postgresql.org/docs/14/datatype-character.html
    """

    def __init__(self, length: int | None = None) -> None:
        self._length = length
        self._sql = "CHAR"
        if length is not None:
            self._sql += f"({length})"

    @property
    def length(self) -> int | None:
        """The length of the string.

        Returns:
            int | None
        """

        return self._length


class Text(SqlType[str]):
    """Variable unlimited length string.

    https://www.postgresql.org/docs/14/datatype-character.html
    """

    _sql = "TEXT"

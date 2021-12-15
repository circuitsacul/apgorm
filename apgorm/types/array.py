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

from typing import TypeVar

from .base_type import SqlType

_T = TypeVar("_T", bound=SqlType)


class Array(SqlType["list[_T]"]):
    def __init__(self, type_: _T, size: int | None = None):
        self._type_ = type_
        self._size = size

        def _get_arrays(
            t: SqlType, arrays: list[Array] | None = None
        ) -> tuple[list[Array], SqlType]:
            arrays = arrays or []
            if isinstance(t, Array):
                arrays.append(t)
                return _get_arrays(t.type_, arrays=arrays)
            else:
                return arrays, t

        arrays, final = _get_arrays(self)

        self.sql = final.sql + "".join(
            [
                ("[]" if a.size is None else f"[{a.size}]")
                for a in reversed(arrays)
            ]
        )

    @property
    def size(self) -> int | None:
        return self._size

    @property
    def type_(self) -> _T:
        return self._type_

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

from typing import Any

from .sql import Block, Raw


class Renderer:
    def __init__(self):
        self._curr_value_id: int = 0

    @property
    def next_value_id(self) -> int:
        self._curr_value_id += 1
        return self._curr_value_id

    def render(self, sql: Block) -> tuple[str, list[Any]]:
        sql_pieces: list[str] = []
        params: list[Any] = []

        for piece in sql.get_pieces(force_wrap=False):
            if isinstance(piece, Raw):
                sql_pieces.append(str(piece))
            else:
                sql_pieces.append(f"${self.next_value_id}")
                params.append(piece.value)

        return " ".join(sql_pieces), params


def render(sql: Block) -> tuple[str, list[Any]]:
    return Renderer().render(sql)

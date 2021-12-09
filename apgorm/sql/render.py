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

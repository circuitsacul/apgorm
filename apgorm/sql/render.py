from __future__ import annotations

from typing import Any

from .sql import Raw, Sql


class Renderer:
    def __init__(self):
        self._curr_value_id: int = 0

    @property
    def next_value_id(self) -> int:
        self._curr_value_id += 1
        return self._curr_value_id

    def render(self, sql: Sql) -> tuple[str, list[Any]]:
        sql_pieces: list[str] = []
        params: list[Any] = []

        for piece in sql.pieces:
            if isinstance(piece, Raw):
                sql_pieces.append(str(piece))
                continue
            sql_pieces.append(f"${self.next_value_id}")
            params.append(piece.value)

        if sql_pieces[0] == "(" and sql_pieces[-1] == ")":
            sql_pieces.pop(0)
            sql_pieces.pop(-1)

        return " ".join(sql_pieces), params


def render(sql: Sql) -> tuple[str, list[Any]]:
    return Renderer().render(sql)

from __future__ import annotations

from .base_type import SqlType


class VarChar(SqlType[str]):
    sql_name = "VARCHAR"

    def __init__(self, n: int):
        self.n = n


class Char(SqlType[str]):
    sql_name = "CHAR"

    def __init__(self, n: int):
        self.n = n


class Text(SqlType[str]):
    sql_name = "TEXT"

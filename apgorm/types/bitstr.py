from __future__ import annotations

import asyncpg

from .base_type import SqlType


class Bit(SqlType[asyncpg.BitString]):
    sql_name = "BIT"

    def __init__(self, n: int):
        self.n = n


class VarBit(SqlType[asyncpg.BitString]):
    sql_name = "BIT VARYING"

    def __init__(self, n: int):
        self.n = n

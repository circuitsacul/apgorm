from __future__ import annotations

from .base_type import SqlType


class Money(SqlType[float]):
    sql_name = "MONEY"

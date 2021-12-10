from __future__ import annotations

from .base_type import SqlType


class Money(SqlType[str]):
    sql_name = "MONEY"

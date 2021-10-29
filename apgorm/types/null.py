from __future__ import annotations

from .base_type import SqlType


class Null(SqlType[None]):
    sql_name = "NULL"

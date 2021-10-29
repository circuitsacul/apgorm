from __future__ import annotations

from .base_type import SqlType


class Boolean(SqlType[bool]):
    sql_name = "BOOLEAN"


Bool = Boolean

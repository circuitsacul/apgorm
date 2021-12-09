from __future__ import annotations

from .base_type import SqlType


class ByteA(SqlType[str]):
    sql_name = "BYTEA"

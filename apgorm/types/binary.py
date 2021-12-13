from __future__ import annotations

from .base_type import SqlType


class ByteA(SqlType[bytes]):
    sql_name = "BYTEA"

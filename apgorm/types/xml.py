from __future__ import annotations

from .base_type import SqlType


class XML(SqlType[str]):
    sql_name = "XML"

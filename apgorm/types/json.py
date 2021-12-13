from __future__ import annotations

from .base_type import SqlType


class Json(SqlType[str]):
    sql_name = "JSON"


class JsonB(SqlType[str]):
    sql_name = "JSON"

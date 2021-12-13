from __future__ import annotations

from typing import TypeVar

from .base_type import SqlType

_T = TypeVar("_T", bound=SqlType)


class Array(SqlType["list[_T]"]):
    sql_name = "ARRAY"

    def __init__(self, type_: _T, size: int | None = None):
        self.type_ = type_
        self.size = size

from __future__ import annotations

from typing import Iterable

from .base_type import SqlType


class Json(SqlType[str]):
    """Stores JSON.

    https://www.postgresql.org/docs/14/datatype-json.html
    """

    __slots__: Iterable[str] = ()

    _sql = "JSON"


class JsonB(SqlType[str]):
    """Stores JSON.

    https://www.postgresql.org/docs/14/datatype-json.html
    """

    __slots__: Iterable[str] = ()

    _sql = "JSONB"

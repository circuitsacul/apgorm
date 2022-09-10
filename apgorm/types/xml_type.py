from __future__ import annotations

from typing import Iterable

from .base_type import SqlType


class XML(SqlType[str]):
    """Type for storing XML data.

    https://www.postgresql.org/docs/14/datatype-xml.html
    """

    __slots__: Iterable[str] = ()

    _sql = "XML"

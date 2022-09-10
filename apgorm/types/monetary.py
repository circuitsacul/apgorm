from __future__ import annotations

from typing import Iterable

from .base_type import SqlType


class Money(SqlType[str]):
    """Currency type, 8 bytes, range -92233720368547758.08 to
    +92233720368547758.07.

    https://www.postgresql.org/docs/14/datatype-money.html
    """

    __slots__: Iterable[str] = ()

    _sql = "MONEY"

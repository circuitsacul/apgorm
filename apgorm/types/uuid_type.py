from __future__ import annotations

import uuid
from typing import Iterable

from .base_type import SqlType


class UUID(SqlType[uuid.UUID]):
    """Universally Unique Identifier (AKA GUID).

    https://www.postgresql.org/docs/14/datatype-uuid.html
    """

    __slots__: Iterable[str] = ()

    _sql = "UUID"

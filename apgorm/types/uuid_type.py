from __future__ import annotations

import uuid

from .base_type import SqlType


class UUID(SqlType[uuid.UUID]):
    sql_name = "UUID"

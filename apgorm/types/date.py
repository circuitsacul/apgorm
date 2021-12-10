from __future__ import annotations

import datetime

from .base_type import SqlType


class Timestamp(SqlType[datetime.datetime]):
    sql_name = "TIMESTAMP"


class Time(SqlType[datetime.time]):
    sql_name = "TIME"


class Interval(SqlType[datetime.timedelta]):
    sql_name = "TIMEDELTA"

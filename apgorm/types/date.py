from __future__ import annotations

import datetime

from .base_type import SqlType


class Timestamp(SqlType[datetime.datetime]):
    sql_name = "TIMESTAMP"


class TimestampZ(SqlType[datetime.datetime]):
    sql_name = "TIMESTAMP WITH TIME ZONE"


class Time(SqlType[datetime.time]):
    sql_name = "TIME"


class TimeZ(SqlType[datetime.time]):
    sql_name = "TIME WITH TIME ZONE"


class Interval(SqlType[datetime.timedelta]):
    sql_name = "TIMEDELTA"

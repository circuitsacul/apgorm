# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import datetime
from enum import Enum

from apgorm.undefined import UNDEF

from .base_type import SqlType


class Timestamp(SqlType[datetime.datetime]):
    def __init__(self, precision: int | UNDEF = UNDEF.UNDEF):
        self._precision = precision
        self.sql = "TIMESTAMP"
        if precision is not UNDEF.UNDEF:
            self.sql += f"({precision})"

    @property
    def precision(self) -> int | UNDEF:
        return self._precision


class TimestampTZ(SqlType[datetime.datetime]):
    def __init__(self, precision: int | UNDEF = UNDEF.UNDEF):
        self._precision = precision
        self.sql = "TIMESTAMPTZ"
        if precision is not UNDEF.UNDEF:
            self.sql += f"({precision})"

    @property
    def precision(self) -> int | UNDEF:
        return self._precision


class Time(SqlType[datetime.time]):
    def __init__(self, precision: int | UNDEF = UNDEF.UNDEF):
        self._precision = precision
        self.sql = "TIME"
        if precision is not UNDEF.UNDEF:
            self.sql += f"({precision})"

    @property
    def precision(self) -> int | UNDEF:
        return self._precision


class TimeTZ(SqlType[datetime.time]):
    def __init__(self, precision: int | UNDEF = UNDEF.UNDEF):
        self._precision = precision
        self.sql = "TIMETZ"
        if precision is not UNDEF.UNDEF:
            self.sql += f"({precision})"

    @property
    def precision(self) -> int | UNDEF:
        return self._precision


class Date(SqlType[datetime.date]):
    sql = "DATE"


class IntervalField(Enum):
    YEAR = "YEAR"
    MONTH = "MONTH"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    SECOND = "SECOND"
    YEAR_TO_MONTH = "YEAR TO MONTH"
    DAY_TO_HOUR = "DAY TO HOUR"
    DAY_TO_SECOND = "DAY TO SECOND"
    HOUR_TO_MINUTE = "HOUR TO MINUTE"
    HOUR_TO_SECOND = "HOUR TO SECOND"
    MINUTE_TO_SECOND = "MINUTE TO SECOND"


class Interval(SqlType[datetime.timedelta]):
    def __init__(
        self,
        interval_field: IntervalField | UNDEF = UNDEF.UNDEF,
        precision: int | UNDEF = UNDEF.UNDEF,
    ):
        self._interval_field = interval_field
        self._precision = precision

        self.sql = "INTERVAL"
        if interval_field is not UNDEF.UNDEF:
            self.sql += " " + interval_field.value
        if precision is not UNDEF.UNDEF:
            self.sql += f"({precision})"

    @property
    def interval_field(self) -> IntervalField | UNDEF:
        return self._interval_field

    @property
    def precision(self) -> int | UNDEF:
        return self._precision

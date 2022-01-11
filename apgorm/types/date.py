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

from .base_type import SqlType


class Timestamp(SqlType[datetime.datetime]):
    """Date and time without time zone.

    Args:
        precision (int, optional): Precision (0-6). Defaults to None.

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    def __init__(self, precision: int | None = None) -> None:
        self._precision = precision
        self._sql = "TIMESTAMP"
        if precision is not None:
            self._sql += f"({precision})"

    @property
    def precision(self) -> int | None:
        """The precision of the timestamp.

        Returns:
            int | None
        """

        return self._precision


class TimestampTZ(SqlType[datetime.datetime]):
    """Date and time with time zone.

    Args:
        precision (int, optional): Precision (0-6). Defaults to None.

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    def __init__(self, precision: int | None = None) -> None:
        self._precision = precision
        self._sql = "TIMESTAMPTZ"
        if precision is not None:
            self._sql += f"({precision})"

    @property
    def precision(self) -> int | None:
        """The precision of the timestamp.

        Returns:
            int | None
        """

        return self._precision


class Time(SqlType[datetime.time]):
    """Time of day with no date or time zone.

    Args:
        precision (int, optional): Precision (0-6). Defaults to None.

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    def __init__(self, precision: int | None = None) -> None:
        self._precision = precision
        self._sql = "TIME"
        if precision is not None:
            self._sql += f"({precision})"

    @property
    def precision(self) -> int | None:
        """The precision of the time.

        Returns:
            int | None
        """

        return self._precision


class TimeTZ(SqlType[datetime.time]):
    """Time of day with time zone (no date).

    Args:
        precision (int, optional): Precision (0-6). Defaults to None.

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    def __init__(self, precision: int | None = None) -> None:
        self._precision = precision
        self._sql = "TIMETZ"
        if precision is not None:
            self._sql += f"({precision})"

    @property
    def precision(self) -> int | None:
        """The precsion of the time.

        Returns:
            int | None
        """

        return self._precision


class Date(SqlType[datetime.date]):
    """Date (no time of day).

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    _sql = "DATE"


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
    """Interval type. Essentially a time range (5 years or 2 minutes) but not
    an actual date or time (05-9-2005).

    Args:
        interval_field (IntervalField, optional): Restrict the fields of
        the interval. Defaults to None.
        precision (int, optional): Precision (0-6). Defaults to None.

    https://www.postgresql.org/docs/14/datatype-datetime.html
    """

    def __init__(
        self,
        interval_field: IntervalField | None = None,
        precision: int | None = None,
    ) -> None:
        self._interval_field = interval_field
        self._precision = precision

        self._sql = "INTERVAL"
        if interval_field is not None:
            self._sql += " " + interval_field.value
        if precision is not None:
            self._sql += f"({precision})"

    @property
    def interval_field(self) -> IntervalField | None:
        """The allowed fields for the interval.

        Returns:
            IntervalField | None
        """

        return self._interval_field

    @property
    def precision(self) -> int | None:
        """The precision of the interval.

        Returns:
            int | None
        """

        return self._precision

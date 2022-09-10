from apgorm.types import (
    Interval,
    IntervalField,
    Time,
    Timestamp,
    TimestampTZ,
    TimeTZ,
)


def test_timestamp_nop():
    ts = Timestamp()
    assert ts.precision is None
    assert ts._sql == "TIMESTAMP"


def test_timestamp_wp():
    ts = Timestamp(5)
    assert ts.precision == 5
    assert ts._sql == "TIMESTAMP(5)"


def test_timestamptz_nop():
    ts = TimestampTZ()
    assert ts.precision is None
    assert ts._sql == "TIMESTAMPTZ"


def test_timestamptz_wp():
    ts = TimestampTZ(5)
    assert ts.precision == 5
    assert ts._sql == "TIMESTAMPTZ(5)"


def test_time_nop():
    t = Time()
    assert t.precision is None
    assert t._sql == "TIME"


def test_time_wp():
    t = Time(5)
    assert t.precision == 5
    assert t._sql == "TIME(5)"


def test_timetz_nop():
    t = TimeTZ()
    assert t.precision is None
    assert t._sql == "TIMETZ"


def test_timetz_wp():
    t = TimeTZ(5)
    assert t.precision == 5
    assert t._sql == "TIMETZ(5)"


def test_interval():
    i = Interval()
    assert i.precision is None
    assert i.interval_field is None
    assert i._sql == "INTERVAL"


def test_interval_wf():
    i = Interval(interval_field=IntervalField.DAY)
    assert i.precision is None
    assert i.interval_field is IntervalField.DAY
    assert i._sql == "INTERVAL DAY"


def test_interval_wp():
    i = Interval(precision=5)
    assert i.precision == 5
    assert i.interval_field is None
    assert i._sql == "INTERVAL(5)"


def test_interval_wpf():
    i = Interval(precision=5, interval_field=IntervalField.DAY)
    assert i.precision == 5
    assert i.interval_field is IntervalField.DAY
    assert i._sql == "INTERVAL DAY(5)"

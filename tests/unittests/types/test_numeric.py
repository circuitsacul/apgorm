import pytest

import apgorm
from apgorm.types import BigSerial, Numeric, Serial, SmallSerial
from apgorm.types.numeric import _BaseSerial


def test_numeric():
    n = Numeric()
    assert n.precision is None
    assert n.scale is None
    assert n._sql == "NUMERIC"


def test_numeric_wp():
    n = Numeric(precision=5)
    assert n.precision == 5
    assert n.scale is None
    assert n._sql == "NUMERIC(5)"


def test_numeric_ws():
    with pytest.raises(apgorm.exceptions.BadArgument):
        Numeric(scale=5)


def test_numeric_wps():
    n = Numeric(scale=4, precision=5)
    assert n.precision == 5
    assert n.scale == 4
    assert n._sql == "NUMERIC(5, 4)"


@pytest.mark.parametrize("s", [Serial, SmallSerial, BigSerial])
def test_serial_subclass_of_base_serial(s):
    assert issubclass(s, _BaseSerial)


@pytest.mark.parametrize("s", [Serial, SmallSerial, BigSerial])
def test_base_serial(s: _BaseSerial):
    nnf = s().field()
    nf = s().nullablefield()

    assert nnf.not_null is True
    assert nf.not_null is False

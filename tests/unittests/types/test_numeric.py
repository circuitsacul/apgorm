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

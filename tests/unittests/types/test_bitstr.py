from __future__ import annotations

from apgorm.types import Bit, VarBit


def test_bit_no_length():
    bit = Bit()
    assert bit._sql == "BIT"
    assert bit._length is None


def test_bit_with_length():
    bit = Bit(5)
    assert bit._sql == "BIT(5)"
    assert bit._length == 5


def test_varbit_no_length():
    bit = VarBit()
    assert bit._sql == "VARBIT"
    assert bit.max_length is None


def test_varbit_with_length():
    bit = VarBit(5)
    assert bit._sql == "VARBIT(5)"
    assert bit.max_length == 5

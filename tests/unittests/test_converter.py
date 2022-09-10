from __future__ import annotations

from enum import IntEnum, IntFlag

from apgorm import IntEFConverter


class IE(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


class IF(IntFlag):
    ONE = 1 << 0
    TWO = 1 << 1
    THREE = 1 << 3


def test_intefconverter_as_intenum() -> None:
    iec = IntEFConverter(IE)
    assert iec.from_stored(3) is IE.THREE
    assert iec.to_stored(IE.THREE) == 3


def test_intefconverter_as_intflag() -> None:
    ifc = IntEFConverter(IF)
    assert ifc.from_stored((IF.ONE | IF.TWO).value) == (IF.ONE | IF.TWO)
    assert ifc.to_stored(IF.ONE | IF.THREE) == (IF.ONE | IF.THREE).value

from __future__ import annotations

from typing import Union

from apgorm.field import Field
from apgorm.undefined import UNDEF

from .base_type import SqlType

INT = Union["SmallInt", "Int", "BigInt"]
FLOAT = Union["Real", "DoublePrecision", "Numeric"]
SERIAL = Union["SmallSerial", "Serial", "BigSerial"]

NUMBER = Union[INT, FLOAT, SERIAL]


class SmallInt(SqlType[int]):
    sql_name = "SMALLINT"


class Int(SqlType[int]):
    sql_name = "INTEGER"


Integer = Int


class BigInt(SqlType[int]):
    sql_name = "BIGINT"


class Numeric(SqlType[int]):
    sql_name = "NUMERIC"


Decimal = Numeric


class Real(SqlType[float]):
    sql_name = "REAL"


class DoublePrecision(SqlType[float]):
    sql_name = "DOUBLE PRECISION"


class SerialField(Field[SqlType[int], Union[int, None]]):
    @property
    def value(self) -> int | None:
        if self._value is UNDEF.UNDEF:
            return None
        return self._value

    @value.setter
    def value(self, other: int):
        self._value = other
        self.changed = True


class SmallSerial(SqlType[int]):
    sql_name = "SMALLSERIAL"
    field_cls = SerialField


class Serial(SqlType[int]):
    sql_name = "SERIAL"
    field_cls = SerialField


class BigSerial(SqlType[int]):
    sql_name = "BIGSERIAL"
    field_cls = SerialField

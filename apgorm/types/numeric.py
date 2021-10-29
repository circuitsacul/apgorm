from __future__ import annotations

from typing import Type, TypeVar, Union

from apgorm.field import Field
from apgorm.sql.sql import Block
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


class SerialField(Field["_BaseSerial", Union[int, None]]):
    @property
    def value(self) -> int | None:
        if self._value is UNDEF.UNDEF:
            return None
        return self._value

    @value.setter
    def value(self, other: int):
        self._value = other
        self.changed = True


_S = TypeVar("_S", bound="_BaseSerial", covariant=True)


class _BaseSerial(SqlType[int]):
    @classmethod
    def field(  # type: ignore
        cls: Type[_S],
        pk: bool = False,
        unique: bool = False,
        references: Block | Field | None = None,
        read_only: bool = False,
    ) -> SerialField:
        return SerialField(
            sql_type=cls(),
            not_null=True,
            pk=pk,
            unique=unique,
            read_only=read_only,
            references=references,
        )

    @classmethod
    def nullfield(  # type: ignore
        cls: Type[_S],
        pk: bool = False,
        unique: bool = False,
        references: Block | Field | None = None,
        read_only: bool = False,
    ) -> SerialField:
        return SerialField(
            sql_type=cls(),
            not_null=False,
            pk=pk,
            unique=unique,
            read_only=read_only,
            references=references,
        )


class SmallSerial(_BaseSerial):
    sql_name = "SMALLSERIAL"


class Serial(_BaseSerial):
    sql_name = "SERIAL"


class BigSerial(_BaseSerial):
    sql_name = "BIGSERIAL"

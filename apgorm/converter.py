from __future__ import annotations

from abc import ABC, abstractmethod
from enum import IntEnum, IntFlag
from typing import Generic, Iterable, Type, TypeVar, Union, cast

_ORIG = TypeVar("_ORIG")
_CONV = TypeVar("_CONV")


class Converter(ABC, Generic[_ORIG, _CONV]):
    """Base class that must be used for all field converters."""

    __slots__: Iterable[str] = ()

    @abstractmethod
    def from_stored(self, value: _ORIG) -> _CONV:
        """Take the value given by the database and convert it to the type
        used in your code."""

    @abstractmethod
    def to_stored(self, value: _CONV) -> _ORIG:
        """Take the type used by your code and convert it to the type
        used to store the value in the database."""


_INTEF = TypeVar("_INTEF", bound="Union[IntFlag, IntEnum]")


class IntEFConverter(Converter[int, _INTEF], Generic[_INTEF]):
    """Converter that converts integers to IntEnums or IntFlags.
    ```
    class User(Model):
        flags = Int().field().with_converter(IntEFConverter(MyIntFlag))
    ```

    Args:
        type_ (Type[IntEnum] | Type[IntFlag]): The IntEnum or IntFlag to use.
    """

    __slots__: Iterable[str] = ("_type",)

    def __init__(self, type_: Type[_INTEF]):
        self._type: Type[_INTEF] = type_

    def from_stored(self, value: int) -> _INTEF:
        return cast(_INTEF, self._type(value))

    def to_stored(self, value: _INTEF) -> int:
        return cast(Union[IntEnum, IntFlag], value).value

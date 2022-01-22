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

from enum import IntEnum, IntFlag
from typing import Generic, Type, TypeVar, Union, cast

_ORIG = TypeVar("_ORIG")
_CONV = TypeVar("_CONV")


class Converter(Generic[_ORIG, _CONV]):
    """Base class that must be used for all field converters."""

    def from_stored(self, value: _ORIG) -> _CONV:
        """Take the value given by the database and convert it to the type
        used in your code."""

        raise NotImplementedError  # pragma: no cover

    def to_stored(self, value: _CONV) -> _ORIG:
        """Take the type used by your code and convert it to the type
        used to store the value in the database."""

        raise NotImplementedError  # pragma: no cover


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

    def __init__(self, type_: Type[_INTEF]):
        self._type: Type[_INTEF] = type_

    def from_stored(self, value: int) -> _INTEF:
        return cast(_INTEF, self._type(value))

    def to_stored(self, value: _INTEF) -> int:
        return cast(Union[IntEnum, IntFlag], value).value

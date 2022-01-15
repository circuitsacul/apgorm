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

from typing import TYPE_CHECKING, Any, Callable, Generic, Type, TypeVar

from .converter import Converter
from .exceptions import BadArgument, InvalidFieldValue, UndefinedFieldValue
from .migrations.describe import DescribeField
from .sql.sql import Comparable, r
from .undefined import UNDEF

if TYPE_CHECKING:  # pragma: no cover
    from .model import Model
    from .sql.sql import Block
    from .types.base_type import SqlType


_SELF = TypeVar("_SELF", bound="BaseField", covariant=True)
_T = TypeVar("_T")
_C = TypeVar("_C")
_F = TypeVar("_F", bound="SqlType")
VALIDATOR = Callable[[_C], bool]


class BaseField(Comparable, Generic[_F, _T, _C]):
    """Represents a field for a table."""

    name: str  # populated by Database
    """The name of the field, populated when Database is initialized."""
    model: Type[Model]  # populated by Database
    """The model this field belongs to, populated when Database is
    initialized."""

    def __init__(
        self,
        sql_type: _F,
        *,
        default: _T | UNDEF = UNDEF.UNDEF,
        default_factory: Callable[[], _T] | None = None,
        not_null: bool = False,
        use_repr: bool = True,
    ) -> None:
        self.sql_type = sql_type

        if (default is not UNDEF.UNDEF) and (default_factory is not None):
            raise BadArgument("Cannot specify default and default_factory.")

        self._default = default
        self._default_factory = default_factory

        self.not_null = not_null

        self.use_repr = use_repr

        self.changed: bool = False
        self._value: _T | UNDEF = UNDEF.UNDEF

        self._validators: list[VALIDATOR[_C]] = []

    @property
    def v(self) -> _C:
        """The current value of the field.

        Raises:
            UndefinedFieldValue: The field value is undefined.
            Probably means that the model has not been created.
        """

        raise NotImplementedError  # pragma: no cover

    @v.setter
    def v(self, other: _C):
        raise NotImplementedError  # pragma: no cover

    @property
    def full_name(self) -> str:
        """The full name of the field (`tablename.fieldname`)."""

        return f"{self.model.tablename}.{self.name}"

    def add_validator(self: _SELF, validator: VALIDATOR[_C]) -> _SELF:
        """Add a validator to the value of this field."""

        self._validators.append(validator)
        return self

    def copy(self) -> BaseField[_F, _T, _C]:
        """Create a copy of the field."""

        n = self.__class__(**self._copy_kwargs())
        if hasattr(self, "name"):
            n.name = self.name
        if hasattr(self, "model"):
            n.model = self.model
        n._validators = self._validators
        return n

    def _validate(self, value: _C) -> None:
        for v in self._validators:
            try:
                if not v(value):
                    raise InvalidFieldValue(
                        f"Validator on {self.name} failed for {value!r}"
                    )
            except InvalidFieldValue:
                raise

    def _describe(self) -> DescribeField:
        return DescribeField(
            name=self.name,
            type_=self.sql_type._sql,
            not_null=self.not_null,
        )

    def _get_default(self) -> _T | UNDEF:
        if self._default is not UNDEF.UNDEF:
            return self._default
        if self._default_factory is not None:
            return self._default_factory()
        return UNDEF.UNDEF

    def _get_block(self) -> Block:
        return r(self.full_name)

    def _copy_kwargs(self) -> dict[str, Any]:
        return dict(
            sql_type=self.sql_type,
            default=self._default,
            default_factory=self._default_factory,
            not_null=self.not_null,
            use_repr=self.use_repr,
        )


class Field(BaseField[_F, _T, _T]):
    @property
    def v(self) -> _T:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self._value

    @v.setter
    def v(self, other: _T):
        self._validate(other)
        self._value = other
        self.changed = True

    def with_converter(
        self, converter: Converter[_T, _C] | Type[Converter[_T, _C]]
    ) -> ConverterField[_F, _T, _C]:
        """Add a converter to the field.

        Args:
            converter (Converter | Type[Converter]): The converter.

        Returns:
            ConverterField: The new field with the converter.
        """

        if isinstance(converter, type) and issubclass(converter, Converter):
            converter = converter()
        f: ConverterField[_F, _T, _C] = ConverterField(
            **self._copy_kwargs(), converter=converter
        )
        if hasattr(self, "name"):
            f.name = self.name
        if hasattr(self, "model"):
            f.model = self.model
        return f


class ConverterField(BaseField[_F, _T, _C]):
    def __init__(self, *args, **kwargs) -> None:
        self.converter: Converter[_T, _C] = kwargs.pop("converter")
        super().__init__(*args, **kwargs)

    @property
    def v(self) -> _C:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self.converter.from_stored(self._value)

    @v.setter
    def v(self, other: _C):
        self._validate(other)
        self._value = self.converter.to_stored(other)
        self.changed = True

    def _copy_kwargs(self) -> dict[str, Any]:
        dct = super()._copy_kwargs()
        dct["converter"] = self.converter
        return dct

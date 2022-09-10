from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Type,
    TypeVar,
    overload,
)

from .converter import Converter
from .exceptions import BadArgument, InvalidFieldValue, UndefinedFieldValue
from .migrations.describe import DescribeField
from .sql.sql import Comparable, raw
from .undefined import UNDEF

if TYPE_CHECKING:  # pragma: no cover
    from .model import Model
    from .sql.sql import Block
    from .types.base_type import SqlType


_SELF = TypeVar("_SELF", bound="BaseField[Any, Any, Any]", covariant=True)
_T = TypeVar("_T")
_C = TypeVar("_C")
_F = TypeVar("_F", bound="SqlType[Any]")
VALIDATOR = Callable[[_C], bool]


class BaseField(Comparable, Generic[_F, _T, _C]):
    """Represents a field for a table."""

    __slots__: Iterable[str] = (
        "name",
        "model",
        "sql_type",
        "_default",
        "_default_factory",
        "not_null",
        "use_repr",
        "_validators",
    )

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

        self._validators: list[VALIDATOR[_C]] = []

    @overload
    def __get__(self: _SELF, inst: None, cls: Type[Model]) -> _SELF:
        ...

    @overload
    def __get__(self, inst: Model, cls: Type[Model]) -> _C:
        ...

    def __get__(
        self: _SELF, inst: Model | None, cls: Type[Model]
    ) -> _SELF | _C:
        raise NotImplementedError

    def __set__(self, inst: Model, value: _C) -> None:
        raise NotImplementedError

    @property
    def full_name(self) -> str:
        """The full name of the field (`tablename.fieldname`)."""

        return f"{self.model.tablename}.{self.name}"

    def add_validator(self: _SELF, validator: VALIDATOR[_C]) -> _SELF:
        """Add a validator to the value of this field."""

        self._validators.append(validator)
        return self

    def _validate(self, value: _C) -> None:
        for v in self._validators:
            if not v(value):
                raise InvalidFieldValue(
                    f"Validator on {self.name} failed for {value!r}"
                )

    def _describe(self) -> DescribeField:
        return DescribeField(
            name=self.name, type_=self.sql_type._sql, not_null=self.not_null
        )

    def _get_default(self) -> _T | UNDEF:
        if self._default is not UNDEF.UNDEF:
            return self._default
        if self._default_factory is not None:
            return self._default_factory()
        return UNDEF.UNDEF

    def _get_block(self) -> Block[SqlType[Any]]:
        return raw(self.full_name)

    def _copy_kwargs(self) -> dict[str, Any]:
        return dict(
            sql_type=self.sql_type,
            default=self._default,
            default_factory=self._default_factory,
            not_null=self.not_null,
            use_repr=self.use_repr,
        )


class Field(BaseField[_F, _T, _T]):
    __slots__: Iterable[str] = ()

    if not TYPE_CHECKING:

        def __get__(self, inst, cls):
            if not inst:
                return self
            if self.name not in inst._raw_values:
                raise UndefinedFieldValue(self)
            return inst._raw_values[self.name]

        def __set__(self, inst, value):
            self._validate(value)
            inst._raw_values[self.name] = value
            inst._changed_fields.add(self.name)

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
    __slots__: Iterable[str] = ("converter",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.converter: Converter[_T, _C] = kwargs.pop("converter")
        super().__init__(*args, **kwargs)

    if not TYPE_CHECKING:

        def __get__(
            self, inst: Model | None, cls: Type[Model]
        ) -> ConverterField | Any:
            if not inst:
                return self
            if self.name not in inst._raw_values:
                raise UndefinedFieldValue(self)
            return self.converter.from_stored(inst._raw_values[self.name])

        def __set__(self, inst, value):
            self._validate(value)
            inst._raw_values[self.name] = self.converter.to_stored(value)
            inst._changed_fields.add(self.name)

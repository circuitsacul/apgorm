from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar

from apgorm.exceptions import ReadOnlyField, UndefinedFieldValue
from apgorm.undefined import UNDEF

if TYPE_CHECKING:
    from apgorm.model import Model
    from apgorm.sql.sql import SQL, Block

    from .types.base_type import SqlType


_T = TypeVar("_T")
_F = TypeVar("_F", bound="SqlType")


class Field(Generic[_F, _T]):
    name: str  # populated by Database
    model: Type[Model]  # populated by Database

    def __init__(
        self,
        sql_type: _F,
        default: SQL[_T] | UNDEF = UNDEF.UNDEF,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        read_only: bool = False,
        references: Block | Field | None = None,
    ):
        self.sql_type = sql_type

        self.default = default

        self.not_null = not_null
        self.pk = pk
        self.unique = unique
        self.references = references

        self.read_only = read_only

        self.changed: bool = False
        self._value: _T | UNDEF = UNDEF.UNDEF

    @property
    def full_name(self) -> str:
        return f"{self.model.tablename}.{self.name}"

    @property
    def value(self) -> _T:
        if self._value is UNDEF.UNDEF:
            raise UndefinedFieldValue(self)
        return self._value

    @value.setter
    def value(self, other: _T):
        if self.read_only:
            raise ReadOnlyField(self)
        self._value = other
        self.changed = True

    def _copy_kwargs(self) -> dict[str, Any]:
        return dict(
            sql_type=self.sql_type,
            default=self.default,
            not_null=self.not_null,
            pk=self.pk,
            unique=self.unique,
            read_only=self.read_only,
            references=self.references,
        )

    def copy(self) -> Field[_F, _T]:
        n = self.__class__(**self._copy_kwargs())
        n.name = self.name
        n.model = self.model
        return n

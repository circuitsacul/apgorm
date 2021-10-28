from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Literal,
    Type,
    TypeVar,
    Union,
    overload,
)

from returns.primitives.hkt import Kind1

from apgorm.undefined import UNDEF

from .types.base_type import SqlType

if TYPE_CHECKING:
    from apgorm.model import Model
    from apgorm.sql.sql import SQL, Sql


_T = TypeVar("_T")
_F = TypeVar("_F", bound="SqlType")
_S = TypeVar("_S", bound="Field")

_MI = TypeVar("_MI")
MAYBEINST = Union[Type[_MI], _MI]


class Field(Generic[_F, _T]):
    name: str  # populated by Database
    model: Type[Model]  # populated by Database

    def __init__(
        self: _S,
        sql_type: Kind1[_F, _T],
        default: SQL[_T] | UNDEF = UNDEF.UNDEF,
        not_null: bool = False,
        pk: bool = False,
        unique: bool = False,
        read_only: bool = False,
        references: Sql | Field[_F, _T] | None = None,
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
            raise Exception("Table not initialized.")  # TODO
        return self._value

    @value.setter
    def value(self, other: _T):
        if self.read_only:
            # TODO
            raise Exception(f"Field {self.full_name} is read-only.")
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


@overload
def field(
    sql_type: Kind1[_F, _T],
    *,
    default: SQL[_T] | UNDEF = UNDEF.UNDEF,
    not_null: Literal[False] = ...,
    pk: bool = False,
    unique: bool = False,
    read_only: bool = False,
    references: Field[_F, _T] | None = None,
) -> Field[_F, _T | None]:
    ...


@overload
def field(
    sql_type: MAYBEINST[Kind1[_F, _T]],
    *,
    default: SQL[_T] | UNDEF = UNDEF.UNDEF,
    not_null: Literal[True],
    pk: bool = False,
    unique: bool = False,
    read_only: bool = False,
    references: Field[_F, _T] | None = None,
) -> Field[_F, _T]:
    ...


def field(
    sql_type: MAYBEINST[Kind1[_F, _T]],
    *,
    default: SQL[_T] | UNDEF = UNDEF.UNDEF,
    not_null: bool = False,
    pk: bool = False,
    unique: bool = False,
    read_only: bool = False,
    references: Field[_F, _T] | None = None,
):
    sqlt: SqlType
    if isinstance(sql_type, SqlType):
        sqlt = sql_type
    else:
        sqlt = sql_type()  # type: ignore

    field_cls = sql_type.field_cls or Field  # type: ignore
    return field_cls(
        sqlt,
        not_null=not_null,
        default=default,
        pk=pk,
        unique=unique,
        read_only=read_only,
        references=references,
    )

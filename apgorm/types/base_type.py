from __future__ import annotations

from typing import Any, Callable, Generic, Iterable, TypeVar

from apgorm.field import Field
from apgorm.undefined import UNDEF

_T = TypeVar("_T", covariant=True)
_S = TypeVar("_S", bound="SqlType[Any]", covariant=True)


class SqlType(Generic[_T]):
    """Base type for all SQL types."""

    __slots__: Iterable[str] = ("_sql",)

    _sql: str
    """The raw sql for the type."""

    def field(
        self: _S,
        default: _T | UNDEF = UNDEF.UNDEF,
        default_factory: Callable[[], _T] | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T]:
        """Generate a field using this type."""

        return Field(
            sql_type=self,
            default=default,
            default_factory=default_factory,
            not_null=True,
            use_repr=use_repr,
        )

    def nullablefield(
        self: _S,
        default: _T | None | UNDEF = UNDEF.UNDEF,
        default_factory: Callable[[], _T] | None = None,
        use_repr: bool = True,
    ) -> Field[_S, _T | None]:
        """Generate a nullable field using this type."""

        return Field(
            sql_type=self,
            default=default,
            default_factory=default_factory,
            not_null=False,
            use_repr=use_repr,
        )

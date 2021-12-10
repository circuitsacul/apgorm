from __future__ import annotations

from typing import Generic, TypeVar

from apgorm.field import Field
from apgorm.sql.sql import SQL, Block
from apgorm.undefined import UNDEF

_T = TypeVar("_T", covariant=True)
_S = TypeVar("_S", bound="SqlType", covariant=True)


class SqlType(Generic[_T]):
    sql_name: str

    def field(
        self: _S,
        default: SQL[_T] | UNDEF = UNDEF.UNDEF,
        pk: bool = False,
        unique: bool = False,
        references: Block | Field | None = None,
        read_only: bool = False,
    ) -> Field[_S, _T]:
        return Field(
            sql_type=self,
            default=default,
            not_null=True,
            pk=pk,
            unique=unique,
            read_only=read_only,
            references=references,
        )

    def nullfield(
        self: _S,
        default: SQL[_T | None] | UNDEF = UNDEF.UNDEF,
        pk: bool = False,
        unique: bool = False,
        references: Block | Field | None = None,
        read_only: bool = False,
    ) -> Field[_S, _T | None]:
        return Field(
            sql_type=self,
            default=default,
            not_null=False,
            pk=pk,
            unique=unique,
            read_only=read_only,
            references=references,
        )

from __future__ import annotations

from typing import TYPE_CHECKING, Type, TypeVar

from returns.primitives.hkt import SupportsKind1

if TYPE_CHECKING:
    from apgorm.field import Field

_T = TypeVar("_T")


class SqlType(SupportsKind1["SqlType", _T]):
    sql_name: str
    field_cls: Type[Field] | None = None

    def as_field(self) -> str:
        return self.sql_name

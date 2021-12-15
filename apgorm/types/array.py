from __future__ import annotations

from typing import TypeVar

from .base_type import SqlType

_T = TypeVar("_T", bound=SqlType)


class Array(SqlType["list[_T]"]):
    # NOTE: must initialize Array to get sql_name

    def __init__(self, type_: _T, size: int | None = None):
        self.type_ = type_
        self.size = size

        def _get_arrays(
            t: SqlType, depth: int = 1, arrays: list[Array] | None = None
        ) -> tuple[int, list[Array], SqlType]:
            arrays = arrays or []
            if isinstance(t, Array):
                arrays.append(t)
                return _get_arrays(t.type_, depth=depth + 1, arrays=arrays)
            else:
                return depth, arrays, t

        dimensions, arrays, final = _get_arrays(self.type_)

        self.sql_name = (
            final.sql_name + "[]" * dimensions
        )  # FIXME: include size

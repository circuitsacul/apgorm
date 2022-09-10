from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence, TypeVar

from .base_type import SqlType

_T = TypeVar("_T")


class Array(SqlType[Sequence[Optional[_T]]]):
    """SQL array type.

    Args:
        subtype (SqlType): The subtype (can be another Array for multiple
        dimensions).

    Example:
    ```
        list_of_names = Array(VarChar(32)).field()
        game_board = Array(Array(Int(), size=16), size=16).nullablefield()
    ```

    https://www.postgresql.org/docs/14/arrays.html
    """

    __slots__: Iterable[str] = ("_subtype",)

    def __init__(self, subtype: SqlType[_T]) -> None:
        self._subtype = subtype

        def _get_arrays(
            t: SqlType[Any], arrays: list[Array[Any]] | None = None
        ) -> tuple[list[Array[Any]], SqlType[Any]]:
            arrays = arrays or []
            if isinstance(t, Array):
                arrays.append(t)
                return _get_arrays(t.subtype, arrays=arrays)
            else:
                return arrays, t

        arrays, final = _get_arrays(self)

        self._sql = final._sql + "".join(["[]" for _ in reversed(arrays)])

    @property
    def subtype(self) -> SqlType[_T]:
        """The arrays sub type.

        Returns:
            SqlType: The sub type.
        """

        return self._subtype

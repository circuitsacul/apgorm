from __future__ import annotations

from typing import (
    Any,
    Callable,
    Generator,
    Generic,
    Iterable,
    Sequence,
    TypeVar,
    overload,
)

_IN = TypeVar("_IN")
_OUT = TypeVar("_OUT")


class LazyList(Generic[_IN, _OUT]):
    """Lazily converts each value of an iterable.

    Incredible useful for casting `list[asyncpg.Record]` to `list[dict]`, and
    then `list[dict]` to `list[Model]`, especially when there are many rows.
    """

    __slots__: Iterable[str] = ("_data", "_converter")

    def __init__(
        self,
        data: Sequence[_IN] | LazyList[Any, _IN],
        converter: Callable[[_IN], _OUT],
    ) -> None:
        self._data = data
        self._converter = converter

    @overload
    def __getitem__(self, index: int) -> _OUT:
        ...  # pragma: no cover

    @overload
    def __getitem__(self, index: slice) -> LazyList[_IN, _OUT]:
        ...  # pragma: no cover

    def __getitem__(self, index: int | slice) -> LazyList[_IN, _OUT] | _OUT:
        if isinstance(index, int):
            return self._converter(self._data[index])
        return LazyList(self._data[index], self._converter)

    def __iter__(self) -> Generator[_OUT, None, None]:
        for r in self._data:
            yield self._converter(r)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        if len(self) == 6:
            ddd = ", {}".format(repr(self[-1]))
        elif len(self) > 6:
            ddd = ", ..., {}".format(repr(self[-1]))
        else:
            ddd = ""
        return "LazyList([{}{}])".format(
            ", ".join(repr(c) for c in list(self[0:5])), ddd
        )

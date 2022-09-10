from __future__ import annotations

from collections import UserString
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Iterable,
    Type,
    TypeVar,
    Union,
    overload,
)

if TYPE_CHECKING:  # pragma: no cover
    from apgorm.field import BaseField
    from apgorm.types.base_type import SqlType
    from apgorm.types.boolean import Bool
    from apgorm.types.numeric import Int  # noqa

_T = TypeVar("_T", covariant=True)
_T2 = TypeVar("_T2")
_SQLT_CO = TypeVar("_SQLT_CO", bound="SqlType[Any]", covariant=True)
_SQLT = TypeVar("_SQLT", bound="SqlType[Any]")
SQL = Union[
    "BaseField[SqlType[_T], _T, Any]",
    "Block[SqlType[_T]]",
    "Parameter[_T]",
    _T,
]
"""
A type alias that allows for any field, raw sql, parameter.

If used like `SQL[int]`, then it must have a python type of int.
For example:

```
integer: SQL[int] = sql(1)  # works
integer: SQL[int] = sql(1).cast(BigInt())  # works
integer: SQL[int] = sql("hi")  # fails
"""

CASTED = Union["BaseField[_SQLT, Any, Any]", "Block[_SQLT]"]
"""
A type alias that allows for any field or raw sql with a specified
SQL type. For example:

```
bigint: CASTED[BigInt] = sql(1).cast(BigInt())  # works
bigint: CASTED[BigInt] = sql(1)  # fails
bigint: CASTED[BigInt] = sql(1).cast(SmallInt())  # fails
```
"""


@overload
def sql(piece: CASTED[_SQLT_CO], /, *, wrap: bool = ...) -> Block[_SQLT_CO]:
    ...


@overload
def sql(piece: SQL[_T2], /, *, wrap: bool = ...) -> Block[SqlType[_T2]]:
    ...


@overload
def sql(*pieces: SQL[Any], wrap: bool = ...) -> Block[Any]:
    ...


def sql(*pieces: SQL[Any], wrap: bool = False) -> Block[Any]:
    """Convenience function to wrap content in a Block.

    It is safe to pass user input to this function.

    Example:
    ```
    sql(
        r("SELECT * FROM mytable WHERE id="),
        5,
        r("AND othercol="),
        "hello",
    ).render()
    # "SELECT * FROM mytable WHERE id=$1 AND othercol=$2", [5, "hello"]
    ```

    Returns:
        Block: The pieces wrapped in a Block.
    """

    return Block(*pieces, wrap=wrap)


def wrap(*pieces: SQL[Any]) -> Block[Any]:
    """Return the SQL pieces as a Block, wrapping them in parantheses."""

    return sql(*pieces, wrap=True)


def join(
    joiner: SQL[Any], *values: SQL[Any], wrap: bool = False
) -> Block[Any]:
    """SQL version of "delim".join(values). For example:

    ```
    join(r(","), value1, value2, value3)
    ```

    Args:
        joiner (SQL): The joiner or deliminator.

    Kwargs:
        wrap (bool): Whether or not to return the result wrapped. Defaults to
        False.
    """

    new_values: list[SQL[Any]] = []
    for x, v in enumerate(values):
        new_values.append(v)
        if x != len(values) - 1:
            new_values.append(joiner)
    return sql(*new_values, wrap=wrap)


def or_(*pieces: SQL[bool]) -> Block[Bool]:
    """Shortcut for `join(r("OR"), value1, value2, ...)`."""

    return join(raw("OR"), *pieces, wrap=True)


def and_(*pieces: SQL[bool]) -> Block[Bool]:
    """Shortcut for `join(r("AND"), value1, value2, ...)`."""

    return join(raw("AND"), *pieces, wrap=True)


def raw(string: str) -> Block[Any]:
    """Treat the string as raw SQL and return a Block.

    Never, ever, ever wrap user input in `r()`. A good rule of thumb is that
    if you see a call to `r()`, the input should be text in quotes, not a
    variable.

    ```
    r(somevarthatmightbeuserinput)  # bad
    r("some text")  # good
    ```
    """

    return sql(Raw(string))


class Raw(UserString):
    __slots__: Iterable[str] = ()


class Parameter(Generic[_T]):
    __slots__: Iterable[str] = ("value",)

    def __init__(self, value: _T) -> None:
        self.value = value


class _Op(Generic[_SQLT]):
    __slots__: Iterable[str] = ("op",)

    def __init__(self, op: str) -> None:
        self.op = op

    def __get__(
        self, inst: object, cls: Type[object]
    ) -> Callable[[SQL[Any]], Block[_SQLT]]:
        def operator(other: SQL[Any]) -> Block[_SQLT]:
            assert isinstance(inst, Comparable)
            return wrap(inst._get_block(), raw(self.op), other)

        return operator


class _Func(Generic[_SQLT]):
    __slots__: Iterable[str] = ("func", "rside")

    def __init__(self, func: str, rside: bool = False) -> None:
        self.func = func
        self.rside = rside

    def __get__(self, inst: object, cls: Type[object]) -> Block[_SQLT]:
        assert isinstance(inst, Comparable)
        if self.rside:
            return wrap(wrap(inst._get_block()), raw(self.func))
        return sql(raw(self.func), wrap(inst._get_block()))


class Comparable:
    __slots__: Iterable[str] = ()

    def _get_block(self) -> Block[Any]:
        raise NotImplementedError  # pragma: no cover

    def cast(self, type_: _SQLT) -> Block[_SQLT]:
        return wrap(self._get_block(), raw("::"), raw(type_._sql))

    # comparison
    is_null = _Func["Bool"]("IS NULL", True)
    is_true = _Func["Bool"]("IS TRUE", True)
    is_false = _Func["Bool"]("IS FALSE", True)
    num_nulls = _Func["Int"]("NUM_NULLS")
    num_nonnulls = _Func["Int"]("NUM_NONNULLS")
    not_ = _Func["Bool"]("NOT")

    eq = _Op["Bool"]("=")
    neq = _Op["Bool"]("!=")
    lt = _Op["Bool"]("<")
    gt = _Op["Bool"](">")
    lteq = _Op["Bool"]("<=")
    gteq = _Op["Bool"](">=")

    any = _Func["Any"]("ANY")
    all = _Func["Any"]("ALL")


class Block(Comparable, Generic[_SQLT_CO]):
    """Represents a list of raw sql and parameters."""

    __slots__: Iterable[str] = ("_pieces", "_wrap")

    def __init__(self, *pieces: SQL[Any] | Raw, wrap: bool = False) -> None:
        """Create a Block. You may find it more convienient to use the `sql()`
        helper function (or `wrap(sql())` if you want the result to be wrapped
        in "( )").

        Kwargs:
            wrap (bool): Whether or not to add `( )` around the result.

        Example:
        ```
        sql = Block(r("SELECT"), "Hello, World", r(","), 17)
        sql.render()  # "SELECT $1, $2", ["Hello, World", 17]
        ```
        """

        self._pieces: list[Raw | Parameter[Any]] = []

        if len(pieces) == 1 and isinstance(pieces[0], Block):
            block = pieces[0]
            assert isinstance(block, Block)
            self._wrap: bool = block._wrap or wrap
            self._pieces = block._pieces

        else:
            self._wrap = wrap
            for p in pieces:
                if isinstance(p, Comparable):
                    p = p._get_block()
                if isinstance(p, Block):
                    self._pieces.extend(p.get_pieces())
                elif isinstance(p, (Raw, Parameter)):
                    self._pieces.append(p)
                else:
                    self._pieces.append(Parameter(p))

    def render(self) -> tuple[str, list[Any]]:
        """Return the rendered result of the Block.

        Returns:
            tuple[str, list[Any]]: The raw SQL (as a string) and the list of
            parameters.
        """

        return Renderer().render(self)

    def render_no_params(self) -> str:
        """Convenience function to get the SQL but not the parameters.

        Although it is technically easier to write `.render()[0]`, this is
        cleaner and more obvious to those reading your code.

        Returns:
            str: The sql.
        """

        return self.render()[0]

    def get_pieces(
        self, force_wrap: bool | None = None
    ) -> list[Raw | Parameter[Any]]:
        wrap = self._wrap if force_wrap is None else force_wrap
        if wrap:
            return [Raw("("), *self._pieces, Raw(")")]
        return self._pieces

    def _get_block(self) -> Block[Any]:
        return self

    def __iadd__(self, other: object) -> Block[Any]:
        if isinstance(other, Block):
            self._pieces.extend(other.get_pieces())
        elif isinstance(other, Parameter):
            self._pieces.append(other)
        else:
            raise TypeError(f"Unsupported type {type(other)}")

        return self


class Renderer:
    __slots__: Iterable[str] = ("_curr_value_id",)

    def __init__(self) -> None:
        self._curr_value_id: int = 0

    @property
    def _next_value_id(self) -> int:
        self._curr_value_id += 1
        return self._curr_value_id

    def render(self, sql: Block[Any]) -> tuple[str, list[Any]]:
        sql_pieces: list[str] = []
        params: list[Any] = []

        for piece in sql.get_pieces(force_wrap=False):
            if isinstance(piece, Raw):
                sql_pieces.append(str(piece))
            else:
                sql_pieces.append(f"${self._next_value_id}")
                params.append(piece.value)

        return " ".join(sql_pieces), params

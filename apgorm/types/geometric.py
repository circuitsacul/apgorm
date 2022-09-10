from __future__ import annotations

from typing import Iterable

import asyncpg

from .base_type import SqlType


class Point(SqlType[asyncpg.Point]):
    """Point (x, y).

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.5
    """

    __slots__: Iterable[str] = ()

    _sql = "POINT"


class Line(SqlType[asyncpg.Line]):
    """Infinite line.

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-LINE
    """

    __slots__: Iterable[str] = ()

    _sql = "LINE"


class LineSegment(SqlType[asyncpg.LineSegment]):
    """Finite line.

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-LSEG
    """

    __slots__: Iterable[str] = ()

    _sql = "LSEG"


class Box(SqlType[asyncpg.Box]):
    """Rectangular box (two points specifying corners).

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.8
    """

    __slots__: Iterable[str] = ()

    _sql = "BOX"


class Path(SqlType[asyncpg.Path]):
    """Path (multiple LineSegments). Can be open or closed. A closed path is
    similar to a polygon.

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.9
    """

    __slots__: Iterable[str] = ()

    _sql = "PATH"


class Polygon(SqlType[asyncpg.Polygon]):
    """Polygon type (similar to a closed path).

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-POLYGON
    """

    __slots__: Iterable[str] = ()

    _sql = "POLYGON"


class Circle(SqlType[asyncpg.Circle]):
    """Circle type (center Point and radius).

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-CIRCLE
    """

    __slots__: Iterable[str] = ()

    _sql = "CIRCLE"

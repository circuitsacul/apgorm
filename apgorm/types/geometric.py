# MIT License
#
# Copyright (c) 2021 TrigonDev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import asyncpg

from .base_type import SqlType


class Point(SqlType[asyncpg.Point]):
    """Point (x, y).

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.5
    """

    _sql = "POINT"


class Line(SqlType[asyncpg.Line]):
    """Infinite line.

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-LINE
    """

    _sql = "LINE"


class LineSegment(SqlType[asyncpg.LineSegment]):
    """Finite line.

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-LSEG
    """

    _sql = "LSEG"


class Box(SqlType[asyncpg.Box]):
    """Rectangular box (two points specifying corners).

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.8
    """

    _sql = "BOX"


class Path(SqlType[asyncpg.Path]):
    """Path (multiple LineSegments). Can be open or closed. A closed path is
    similar to a polygon.

    https://www.postgresql.org/docs/14/datatype-geometric.html#id-1.5.7.16.9
    """

    _sql = "PATH"


class Polygon(SqlType[asyncpg.Polygon]):
    """Polygon type (similar to a closed path).

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-POLYGON
    """

    _sql = "POLYGON"


class Circle(SqlType[asyncpg.Circle]):
    """Circle type (center Point and radius).

    https://www.postgresql.org/docs/14/datatype-geometric.html#DATATYPE-CIRCLE
    """

    _sql = "CIRCLE"

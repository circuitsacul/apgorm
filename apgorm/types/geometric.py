from __future__ import annotations

import asyncpg

from .base_type import SqlType


class Point(SqlType[asyncpg.Point]):
    sql_name = "POINT"


class Line(SqlType[asyncpg.Line]):
    sql_name = "LINE"


class LineSegment(SqlType[asyncpg.LineSegment]):
    sql_name = "LSEG"


class Box(SqlType[asyncpg.Box]):
    sql_name = "BOX"


class Path(SqlType[asyncpg.Path]):
    sql_name = "PATH"


class Polygon(SqlType[asyncpg.Polygon]):
    sql_name = "POLYGON"


class Circle(SqlType[asyncpg.Circle]):
    sql_name = "CIRCLE"

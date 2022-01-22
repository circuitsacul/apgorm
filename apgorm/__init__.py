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

"""
apgorm is a full type-checked asynchronous ORM wrapped around asyncpg.

apgorm is licensed under the MIT license.

https://github.com/TrigonDev/apgorm
"""

from importlib import metadata

from . import exceptions
from .connection import Connection, Pool, PoolAcquireContext
from .constraints.check import Check
from .constraints.constraint import Constraint
from .constraints.exclude import Exclude
from .constraints.foreign_key import ForeignKey, ForeignKeyAction
from .constraints.primary_key import PrimaryKey
from .constraints.unique import Unique
from .converter import Converter, IntEFConverter
from .database import Database
from .field import BaseField, ConverterField, Field
from .indexes import Index, IndexType
from .manytomany import ManyToMany
from .migrations.describe import (
    Describe,
    DescribeConstraint,
    DescribeField,
    DescribeIndex,
    DescribeTable,
)
from .migrations.migration import Migration
from .model import Model
from .sql.query_builder import (
    BaseQueryBuilder,
    DeleteQueryBuilder,
    FetchQueryBuilder,
    FilterQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
)
from .sql.sql import (
    CASTED,
    SQL,
    Block,
    Comparable,
    Parameter,
    Raw,
    Renderer,
    and_,
    join,
    or_,
    r,
    sql,
    wrap,
)
from .undefined import UNDEF
from .utils.lazy_list import LazyList

__version__ = metadata.version(__name__)

__all__ = (
    "Converter",
    "Model",
    "Database",
    "ManyToMany",
    "Constraint",
    "Check",
    "ForeignKey",
    "ForeignKeyAction",
    "PrimaryKey",
    "Exclude",
    "Unique",
    "Index",
    "IndexType",
    "Migration",
    "Describe",
    "DescribeConstraint",
    "DescribeTable",
    "DescribeField",
    "DescribeIndex",
    "CASTED",
    "SQL",
    "Block",
    "Comparable",
    "Parameter",
    "Raw",
    "Renderer",
    "BaseQueryBuilder",
    "FetchQueryBuilder",
    "DeleteQueryBuilder",
    "FilterQueryBuilder",
    "InsertQueryBuilder",
    "UpdateQueryBuilder",
    "LazyList",
    "Connection",
    "Pool",
    "Field",
    "BaseField",
    "ConverterField",
    "PoolAcquireContext",
    "IntEFConverter",
    "UNDEF",
    "and_",
    "join",
    "or_",
    "r",
    "sql",
    "wrap",
    "types",
    "migrations",
    "exceptions",
    "undefined",
)

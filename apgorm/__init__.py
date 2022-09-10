"""
apgorm is a fully type-checked asynchronous ORM wrapped around asyncpg.

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
    raw,
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
    "raw",
    "sql",
    "wrap",
    "types",
    "migrations",
    "exceptions",
    "undefined",
)

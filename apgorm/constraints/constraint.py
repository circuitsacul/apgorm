from typing import Any, Iterable

from apgorm.migrations.describe import DescribeConstraint
from apgorm.sql.sql import Block


class Constraint:
    """The base class for all constraints."""

    __slots__: Iterable[str] = ("name",)

    name: str
    """The name of the constraint.

    Populated by Database and will not exist until an instance
    of Database has been created."""

    def _creation_sql(self) -> Block[Any]:
        raise NotImplementedError  # pragma: no cover

    def _describe(self) -> DescribeConstraint:
        return DescribeConstraint(
            name=self.name, raw_sql=self._creation_sql().render_no_params()
        )

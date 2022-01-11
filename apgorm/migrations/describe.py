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

from typing import List

from pydantic import BaseModel


class DescribeField(BaseModel):
    """Field description."""

    name: str
    """The name of the field."""
    type_: str
    """The raw SQL name of the type (INTEGER, VARCHAR, etc.)."""
    not_null: bool
    """Whether or not the field should be marked NOT NULL."""


class DescribeConstraint(BaseModel):
    """Constraint description."""

    name: str
    """The name of the constraint."""
    raw_sql: str
    """The raw SQL of the constraint."""


class DescribeIndex(BaseModel):
    """Index description."""

    name: str
    """The name of the index."""
    raw_sql: str
    """The raw SQL of the index."""


class DescribeTable(BaseModel):
    """Table description."""

    name: str
    """The name of the table."""
    fields: List[DescribeField]
    """List of field descriptions."""
    fk_constraints: List[DescribeConstraint]
    """List of ForeignKey descriptions."""
    pk_constraint: DescribeConstraint
    """List of PrimaryKey descriptions."""
    unique_constraints: List[DescribeConstraint]
    """List of Unique descriptions."""
    check_constraints: List[DescribeConstraint]
    """List of Check descriptions."""
    exclude_constraints: List[DescribeConstraint]
    """List of Exclude descriptions."""

    @property
    def constraints(self) -> List[DescribeConstraint]:
        """List of all constraints (FK, PK, unique, check, and exclude).

        Returns:
            List[DescribeConstraint]: List of constraints.
        """

        return (
            self.fk_constraints
            + [self.pk_constraint]
            + self.unique_constraints
            + self.check_constraints
            + self.exclude_constraints
        )


class Describe(BaseModel):
    """Database description."""

    tables: List[DescribeTable]
    """List of table descriptions."""
    indexes: List[DescribeIndex]
    """List of index descriptions."""

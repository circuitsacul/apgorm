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

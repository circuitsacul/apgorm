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

from typing import List, Union

from pydantic import BaseModel


class DescribeField(BaseModel):
    name: str
    type_: str
    not_null: bool
    default: Union[str, None] = None


class DescribeConstraint(BaseModel):
    name: str
    raw_sql: str


class DescribeTable(BaseModel):
    name: str
    fields: List[DescribeField]
    fk_constraints: List[DescribeConstraint]
    pk_constraint: DescribeConstraint
    unique_constraints: List[DescribeConstraint]
    check_constraints: List[DescribeConstraint]

    @property
    def constraints(self) -> List[DescribeConstraint]:
        return (
            self.fk_constraints
            + [self.pk_constraint]
            + self.unique_constraints
            + self.check_constraints
        )


class Describe(BaseModel):
    tables: List[DescribeTable]

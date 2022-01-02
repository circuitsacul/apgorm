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

from apgorm.migrations.describe import DescribeConstraint
from apgorm.sql.sql import Block


class Constraint:
    name: str  # populated by database

    def creation_sql(self) -> Block:
        raise NotImplementedError

    def describe(self) -> DescribeConstraint:
        raw_sql, params = self.creation_sql().render()
        if len(params) > 0:
            raise Exception(
                f'{self.__class__.__name__} constraint "{self.name}" '
                "received parameters, but ALTER TABLE does not accept "
                "parameters. Please modify the constraint to remove these "
                "parameters (write them as raw sql).\nThe parameters were: "
                + "\n - ".join([str(p) for p in params])
            )
        return DescribeConstraint(
            self.name,
            raw_sql,
        )

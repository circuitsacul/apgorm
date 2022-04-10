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

import pytest

import apgorm
from apgorm.sql.generators import query
from apgorm.sql.sql import Block
from apgorm.types import VarChar


class MyModel(apgorm.Model):
    somefield = VarChar(32).field()
    primary_key = (somefield,)


class Database(apgorm.Database):
    mymodel = MyModel


DB = Database(None)


@pytest.mark.parametrize("model", [MyModel, MyModel(), apgorm.raw("mymodel")])
def test_select_table_model(model):
    q = query.select(from_=model)
    assert q.render() == ("SELECT * FROM mymodel", [])


@pytest.mark.parametrize(
    "fields",
    [
        [apgorm.raw("somefield"), MyModel.somefield],
        [apgorm.raw("somefield")],
        [MyModel.somefield],
    ],
)
def test_select_table_fields(fields):
    q = query.select(from_=MyModel, fields=fields)
    fs = [
        f.render_no_params() if isinstance(f, Block) else f.full_name
        for f in fields
    ]
    fs = " , ".join(fs)
    assert q.render() == (f"SELECT ( {fs} ) FROM mymodel", [])


def test_where_logic():
    q = query.select(from_=MyModel, where=apgorm.raw("name=$1"))
    assert q.render() == ("SELECT * FROM mymodel WHERE ( name=$1 )", [])


def test_count():
    q = query.select(from_=MyModel, count=True)
    assert q.render() == ("SELECT COUNT(*) FROM mymodel", [])

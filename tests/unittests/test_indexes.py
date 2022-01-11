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

from apgorm import Database, Index, IndexType, Model
from apgorm.exceptions import BadArgument
from apgorm.types import VarChar


class SomeModel(Model):
    name = VarChar(32).field()
    other = VarChar(32).field()
    primary_key = (name,)


class MyDb(Database):
    some_model = SomeModel


DB = MyDb(None)


def test_creation():
    # single field
    single_index = Index(SomeModel, SomeModel.name)
    assert single_index.fields == [SomeModel.name]

    # multiple fields
    multi_index = Index(SomeModel, [SomeModel.name, SomeModel.other])
    assert multi_index.fields == [SomeModel.name, SomeModel.other]

    # test 0 field error
    try:
        Index(SomeModel, [])
    except BadArgument:
        pass
    else:
        assert False, "Didn't raise BadArgument."

    # test other exceptions
    for t in IndexType:
        try:
            Index(SomeModel, [SomeModel.name, SomeModel.other], type_=t)
        except BadArgument:
            multi = False
        else:
            multi = True

        try:
            Index(SomeModel, SomeModel.name, unique=True, type_=t)
        except BadArgument:
            unique = False
        else:
            unique = True

        assert multi == t.value.multi
        assert unique == t.value.unique


def test_get_name():
    single_index = Index(SomeModel, SomeModel.name)
    multi_index = Index(SomeModel, [SomeModel.name, SomeModel.other])

    assert single_index.get_name() == "_btree_index_some_model__name"
    assert multi_index.get_name() == "_btree_index_some_model__name_other"

from __future__ import annotations

import pytest

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
    with pytest.raises(BadArgument):
        Index(SomeModel, [])

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

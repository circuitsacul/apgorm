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

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
from apgorm import (
    DeleteQueryBuilder,
    FetchQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
)
from apgorm.sql.query_builder import _dict_model_converter

ALL_BUILDERS = [
    DeleteQueryBuilder,
    FetchQueryBuilder,
    InsertQueryBuilder,
    UpdateQueryBuilder,
]
FILTER_BUILDERS = [DeleteQueryBuilder, FetchQueryBuilder, UpdateQueryBuilder]


def test_model_converter(mocker):
    c = _dict_model_converter(m := mocker.Mock())
    ret = c({"hello": "world"})

    assert m._from_raw.return_value is ret
    m._from_raw.assert_called_once_with(hello="world")


@pytest.mark.parametrize("type_", ALL_BUILDERS)
def test_init_no_con(type_, mocker):
    q = type_(m := mocker.Mock())
    assert q.model is m
    assert q.con is m.database


@pytest.mark.parametrize("type_", ALL_BUILDERS)
def test_init_with_con(type_, mocker):
    q = type_(m := mocker.Mock(), c := mocker.Mock())
    assert q.model is m
    assert q.con is c


@pytest.mark.parametrize("type_", FILTER_BUILDERS)
def test_where_logic(type_, mocker):
    q = type_(mocker.Mock())
    q.where("PARAM", key="value")

    assert q._where_logic().render() == (
        "$1 AND ( key = $2 )",
        ["PARAM", "value"],
    )


@pytest.mark.parametrize("type_", FILTER_BUILDERS)
def test_where_logic_empty(type_, mocker):
    q = type_(mocker.Mock())

    assert q._where_logic() is None


@pytest.mark.parametrize("type_", FILTER_BUILDERS)
def test_where_returns_self(type_, mocker):
    q = type_(mocker.Mock())
    nq = q.where()

    assert q is nq


@pytest.mark.parametrize("reverse", [True, False])
def test_fqb_order_by(mocker, reverse):
    q = FetchQueryBuilder(mocker.Mock())
    q.order_by("hello, world", reverse=reverse)

    assert q._reverse is reverse
    assert q._order_by_logic == "hello, world"


def test_fqb_order_by_returns_self(mocker):
    q = FetchQueryBuilder(mocker.Mock())
    nq = q.order_by("hello, world")

    assert q is nq


def test_fqb_exists(mocker):
    q = FetchQueryBuilder(m := mocker.Mock())
    m.tablename = "tablename"

    f = mocker.patch.object(q, "_get_block")
    f.return_value = apgorm.raw("hello")

    assert q.exists().render() == ("EXISTS ( hello )", [])


@pytest.mark.asyncio
async def test_fqb_fetchmany_exc(mocker):
    q = FetchQueryBuilder(mocker.Mock())

    with pytest.raises(TypeError):
        await q.fetchmany("hello")


@pytest.mark.asyncio
async def test_fqb_fetchmany(mocker):
    q = FetchQueryBuilder(m := mocker.Mock(), c := mocker.AsyncMock())
    c.fetchmany.return_value = [{"hello": "world"}]

    ll = await q.fetchmany()
    cnv = ll[0]
    assert ll._data == [{"hello": "world"}]
    assert cnv is m._from_raw.return_value
    m._from_raw.assert_called_once_with(hello="world")

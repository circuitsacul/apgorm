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

import pytest
from pytest_mock import MockerFixture

from apgorm import Converter, Field
from apgorm.exceptions import (
    BadArgument,
    InvalidFieldValue,
    UndefinedFieldValue,
)


@pytest.fixture(scope="function")
def mock_field(mocker: MockerFixture):
    f = Field(mocker.Mock())
    f.sql_type.sql = "SQLTYPE"
    f.model = mocker.Mock()
    f.model.tablename = "table"
    f.name = "field"
    return f


def test_init():
    Field(None)
    try:
        Field(None, default=None, default_factory=lambda: 1)
    except BadArgument:
        pass
    else:
        assert False, "Didn't raise BadArgument."


def test_full_name(mock_field: Field):
    assert mock_field.full_name == "table.field"


def test_add_validator(mock_field: Field, mocker: MockerFixture):
    validator = mocker.Mock()
    ret_f = mock_field.add_validator(validator)

    assert ret_f is mock_field
    assert validator in mock_field._validators


def test_validate(mock_field: Field, mocker: MockerFixture):
    works = mocker.Mock()
    works.return_value = True
    fails = mocker.Mock()
    fails.return_value = False

    def fails_another_way(v):
        raise InvalidFieldValue("Test")

    assert mock_field.add_validator(works)._validate(None) is None

    with pytest.raises(InvalidFieldValue):
        mock_field.add_validator(fails)._validate(None)

    mock_field._validators = []
    try:
        mock_field.add_validator(fails_another_way)._validate(None)
    except InvalidFieldValue:
        pass
    else:
        assert False, "Raising Exception didn't raise InvalidFieldValue."

    # test that Field.v = value calls validators
    validator = mocker.Mock()
    mock_field._validators = [validator]
    mock_field.v = 1
    validator.assert_called_once_with(1)


def test_copy(mock_field: Field):
    cp = mock_field.copy()

    assert cp is not mock_field
    assert cp.model is mock_field.model
    assert cp._copy_kwargs() == mock_field._copy_kwargs()
    assert cp.name == mock_field.name


def test_value(mock_field: Field):
    with pytest.raises(UndefinedFieldValue):
        mock_field.v

    mock_field.v = "hello"

    assert mock_field.v == "hello"
    assert mock_field.changed


class MyConv(Converter):
    def to_stored(self, value: str) -> int:
        return int(value)

    def from_stored(self, value: int) -> str:
        return str(value)


def test_with_converter(mock_field: Field, mocker: MockerFixture):
    to_stored_spy = mocker.spy(MyConv, "to_stored")
    from_stored_spy = mocker.spy(MyConv, "from_stored")

    convf_init = mock_field.with_converter(i := MyConv())
    convf_type = mock_field.with_converter(MyConv)

    with pytest.raises(UndefinedFieldValue):
        convf_init.v

    convf_init.v = "1"
    convf_type.v = "1"

    assert convf_init.v == "1"
    assert convf_type.v == "1"
    to_stored_spy.assert_any_call(i, "1")
    to_stored_spy.assert_any_call(convf_type.converter, "1")
    from_stored_spy.assert_any_call(i, 1)
    from_stored_spy.assert_any_call(convf_type.converter, 1)


def test_converter_field_copy(mock_field: Field):
    field = mock_field.with_converter(MyConv())
    cp = field.copy()

    assert cp is not field
    assert cp._copy_kwargs() == field._copy_kwargs()
    assert cp.model is field.model
    assert cp.name == field.name

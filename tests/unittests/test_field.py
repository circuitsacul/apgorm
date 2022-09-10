import pytest
from pytest_mock import MockerFixture

from apgorm import Converter, Field
from apgorm.exceptions import BadArgument, InvalidFieldValue


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
    with pytest.raises(BadArgument):
        Field(None, default=None, default_factory=lambda: 1)


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
    mock_field._validate(1)
    validator.assert_called_once_with(1)


class MyConv(Converter):
    def to_stored(self, value: str) -> int:
        return int(value)

    def from_stored(self, value: int) -> str:
        return str(value)


def test_with_converter(mock_field: Field):
    convf_init = mock_field.with_converter(i := MyConv())
    convf_type = mock_field.with_converter(MyConv)

    assert convf_init.converter is i
    assert isinstance(convf_type.converter, MyConv)

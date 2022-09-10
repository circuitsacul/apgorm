import pytest

from apgorm.types import Array, Int  # for subtypes


@pytest.mark.parametrize("subtype", [Int(), Array(Int()), Array(Array(Int()))])
def test_array_init(subtype):
    a = Array(subtype)

    assert a.subtype is subtype


def test_array_sql():
    assert Array(Int())._sql == "INTEGER[]"
    assert Array(Array(Int()))._sql == "INTEGER[][]"

from apgorm.types import Char, VarChar


def test_char_no_length():
    c = Char()
    assert c.length is None
    assert c._sql == "CHAR"


def test_char_with_length():
    c = Char(5)
    assert c.length == 5
    assert c._sql == "CHAR(5)"


def test_varchar_no_length():
    c = VarChar()
    assert c.max_length is None
    assert c._sql == "VARCHAR"


def test_varchar_with_length():
    c = VarChar(5)
    assert c.max_length == 5
    assert c._sql == "VARCHAR(5)"

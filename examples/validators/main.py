from __future__ import annotations

from pathlib import Path

import apgorm
from apgorm.exceptions import InvalidFieldValue
from apgorm.types import VarChar


def email_validator(email: str | None) -> bool:
    if email is None or email.endswith("@gmail.com"):
        return True
    raise InvalidFieldValue("Email must be None or end with @gmail.com")


class User(apgorm.Model):
    username = VarChar(32).field()
    email = VarChar(32).nullablefield()
    email.add_validator(email_validator)

    primary_key = (username,)


class Database(apgorm.Database):
    users = User


def main() -> None:
    Database(Path("examples/validators/migrations"))

    user = User(username="Circuit")
    try:
        user.email = "not an email"
    except InvalidFieldValue:
        print("'not an email' is not a valid email!")

    user.email = "something@gmail.com"
    print(f"{user.email} is a valid email!")

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

from pathlib import Path

import apgorm
from apgorm.exceptions import InvalidFieldValue
from apgorm.types.character import VarChar


class User(apgorm.Model):
    username = VarChar(32).field()
    email = VarChar(32).nullablefield()
    email.add_validator(
        lambda email: email is None or email.endswith("@gmail.com")
    )

    primary_key = (username,)


class Database(apgorm.Database):
    users = User


def main():
    Database(Path("examples/validators/migrations"))

    user = User(username="Circuit")
    try:
        user.email.v = "not an email"
    except InvalidFieldValue:
        print("'not an email' is not a valid email!")

    user.email.v = "something@gmail.com"
    print(f"{user.email.v} is a valid email!")

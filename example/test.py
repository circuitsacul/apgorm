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

import asyncio

import apgorm
from apgorm.exceptions import UndefinedFieldValue
from apgorm.sql.generators.comp import lt
from apgorm.types.boolean import Boolean
from apgorm.types.numeric import Integer


class User(apgorm.Model):
    tablename = "users"

    age = Integer().field(default=0)
    is_cool = Boolean().field(default=False)

    def __repr__(self) -> str:
        try:
            return (
                f"User AGE:{self.age.value} "
                f"IS_COOL:{self.is_cool.value} ({self.uid.value})"
            )
        except UndefinedFieldValue:
            return f"User AGE:UNKOWN IS_COOL:UNKOWN ({self.uid.value})"


class Database(apgorm.Database):
    user = User


async def main():
    db = Database()
    await db.connect(database="apgorm")
    try:
        await _main(db)
    finally:
        await db.cleanup()


async def _main(db: Database):
    def head():
        print("#" * 50 + "\n")

    user = User(age=3, is_cool=True)
    print(user)
    await user.create()
    print(user)
    await user.delete()

    head()
    ages = [3, 9, 2, 16]
    is_cools = [True, True, False, True]
    for age, is_cool in zip(ages, is_cools):
        await User(age=age, is_cool=is_cool).create()

    head()
    all_users = await User.fetch_query().fetchmany()
    print(all_users)

    head()
    cool_users = await User.fetch_query().where(is_cool=True).fetchmany()
    print(cool_users)

    head()
    young_users = await User.fetch_query().where(lt(User.age, 10)).fetchmany()
    print(young_users)

    head()
    for user in young_users:
        user.age.value = 11
        await user.save()

    head()
    print(await User.fetch_query().fetchmany())

    head()
    await User.delete_query().execute()


if __name__ == "__main__":
    asyncio.run(main())

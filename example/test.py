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
    def head():
        print("#" * 50 + "\n")

    db = Database()
    await db.connect(database="apgorm")

    user = User(age=3, is_cool=True)
    print(user)
    await user.create()
    print(user)
    await user.delete()

    head()
    ages = [3, 9, 2, 16]
    is_cool = [True, True, False, True]
    for age, is_cool in zip(ages, is_cool):
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

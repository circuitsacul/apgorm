import asyncio

import apgorm
from apgorm.sql import Block, render
from apgorm.sql.generators.comp import neq
from apgorm.sql.generators.query import cast, r
from apgorm.types.numeric import Integer


class User(apgorm.Model):
    tablename = "users"

    some_id = Integer.field(default=5)

    def __repr__(self) -> str:
        try:
            return f"User {self.some_id.value} ({self.uid.value})"
        except Exception:  # TODO: TableNotInitialized Exception
            return f"User UNKOWN ({self.uid.value})"


class Database(apgorm.Database):
    user = User


async def single_row() -> None:
    print("#" * 25)
    print("SINGLE ROW:\n")

    user_to_make = User()
    print(user_to_make)

    await user_to_make.create()
    print(user_to_make)

    user_to_make = await User.fetch(uid=user_to_make.uid.value)
    print(user_to_make)

    user_to_make.some_id.value = 0
    await user_to_make.save()
    print(user_to_make)

    await user_to_make.delete()


async def many_rows() -> None:
    print("\n" + "#" * 25)
    print("MANY ROWS:\n")

    for i in range(0, 10):
        await User(some_id=i).create()
    await User(some_id=-1).create()

    print(await User.fetch_query().fetchmany())

    q = User.fetch_query()
    q.where(some_id=-1)
    print(await q.fetchone())

    q = User.fetch_query()
    q.where(neq(User.some_id, -1))
    print(await q.fetchmany())

    await User.delete_query().execute()


async def custom_queries(db: Database) -> None:
    sql = Block[Integer](r("SELECT"), cast(1, Integer))
    print(await db.fetchval(*render(sql)))


async def main() -> None:
    db = Database()
    await db.connect(database=input("Database Name: "))
    await single_row()
    await many_rows()
    await custom_queries(db)


if __name__ == "__main__":
    asyncio.run(main())

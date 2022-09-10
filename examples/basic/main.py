from __future__ import annotations

from pathlib import Path

import apgorm
from apgorm.types import VarChar


class User(apgorm.Model):
    username = VarChar(32).field()
    nickname = VarChar(32).nullablefield()

    primary_key = (username,)


class Database(apgorm.Database):
    users = User


async def _main() -> None:
    await User.delete_query().execute()

    # create a user
    user = await User(username="Circuit").create()
    print("Created", user)

    # get the user
    _u = await User.fetch(username="Circuit")
    print(f"{user} == {_u}:", user == _u)

    # delete the user
    await user.delete()
    print("Deleted", user)

    # create lots of users
    for un in ["Circuit", "Bad Guy", "Super Man", "Batman"]:
        await User(username=un).create()
        print("Created user with name", un)

    # get all users except for "Bad Guy"
    query = User.fetch_query()
    query.where(User.username.neq("Bad Guy"))
    query.order_by(User.username.eq("Circuit"), True)  # put Circuit first
    good_users = await query.fetchmany()
    print("Users except for 'Bad Guy':", good_users)

    # set the nickname for all good users to "Good Guy"
    for user in good_users:
        user.nickname = "Good Guy"
        await user.save()

    # OR, you can use User.update_query...
    (
        await User.update_query()
        .where(User.username.neq("Bad Guy"))
        .set(nickname="Good Guy")
        .execute()
    )

    print(
        "Users after setting nicknames:", await User.fetch_query().fetchmany()
    )


async def main() -> None:
    db = Database(Path("examples/basic/migrations"))
    await db.connect(database="apgorm_testing_database")

    if db.must_create_migrations():
        db.create_migrations()
    if await db.must_apply_migrations():
        await db.apply_migrations()

    try:
        await _main()
    finally:
        await db.cleanup()

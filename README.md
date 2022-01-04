# apgorm
An ORM wrapped around asyncpg. Examples can be found under `examples/`. Run examples with `python -m examples.<example_name>` (`python -m examples.basic`).

Please note that this library is not for those learning SQL or Postgres. Although the basic usage of apgorm is straightforward, you will run into problems, especially with migrations, if you don't understand regular SQL well.

## Features
 - Fully type-checked
 - Fairly straightforward and easy-to-use
 - Migration support

## Limitations
 - There are limitations on what the name of a column can be. For example, you cannot have a column named `tablename` since that is used to declare the name of the model.
 - `apgorm` only supports PostgreSQL with asyncpg (although I'd be interested to see if anyone wants to fork apgorm for use with another library/database).
 - Doesn't support python migrations. This means that you can't create your own migration file with python code.

## Basic Usage
Defining a model and database:
```py
class User(apgorm.Model):
    username = VarChar(32).field()
    email = VarChar().nullablefield()
    
    primary_key = (username,)
    
class Database(apgorm.Database):
    users = User
```

Intializing the database:
```py
db = Database(migrations_folder=pathlib.Path("path/to/migrations"))
await db.connect(database="database name")
```

Creating & Applying migrations:
```py
if db.must_create_migrations():
    db.create_migrations()
if await db.must_apply_migrations():
    await db.apply_migrations()
```

Basic create, fetch, update, and delete:
```py
user = User(username="Circuit")
await user.create()
print("Created user", user)

assert user == await User.fetch(username="Circuit")

user.email.v = "email@example.com"
await user.save()

await user.delete()
```

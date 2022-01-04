# apgorm
An ORM wrapped around asyncpg. Examples can be found under `examples/`. Run examples with `python -m examples.<example_name>` (`python -m examples.advanced`).

Please note that this library is not for those learning SQL or Postgres. Although the basic usage of apgorm is straightforward, you will run into problems, especially with migrations, if you don't understand regular SQL well.

## Features
These are features that will exist by the first release of apgorm:
 - Fully type-checked
 - 100% code coverage
 - Fairly straightforward and easy-to-use
 - Migration support

## Limitations
There are some limitations that should be noted:
 - There are limitations on what the name of a column can be. For example, you cannot have a column named `tablename` since that is used to declare the name of the model.
 - `apgorm` only supports PostgreSQL with asyncpg (although I'd be interested to see if anyone wants to fork apgorm for use with another library/database).
 - Doesn't support python migrations. This means that you can't create your own migration file with python code.
 - Doesn't support automatic field/table renaming. You can do this manually by creating your own migration (See "Manual Migrations")

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

## Manual Migrations
The migration system is such that you can create your own migrations. You should only need to do this for complex migrations (changing a field data type, renaming tables/fields, etc.)

 1. Make the changes to the Database, if any are needed.
 2. First make sure that migrations are up-to-date by running `db.create_migrations()`
 3. Go to the migrations folder and create a folder with the next migration id (whatever the highest id is plus one)
 4. Create a file called `describe.json`. Call `db.describe().todict()` and copy the output to `describe.json`.
 5. Create a file called `migrations.sql` and put any sql you want for migrations.

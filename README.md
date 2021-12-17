# asyncpg-orm
 An ORM wrapped around asyncpg. An advanced example can be found at `examples/example.py`.

## Features
 - Fully type-checked
 - Easy-to-use
 - Migration support

## Limitations
There are some limitations that should be noted:
 - All models *must* have a `id_` field. The type of the field is a `Serial` by default, but this can be changed. The `id_` field cannot be removed, however.
 - There are limitations on what the name of a column can be. For example, you cannot have a column named `tablename` since that is used to declare the name of the model.
 - apgorm only supports PostgreSQL with asyncpg (although I'd be interested to see if anyone wants to fork apgorm for use with another library/database).

# apgorm
An ORM wrapped around asyncpg. Examples can be found under `examples/`. Run examples with `python -m examples.<example_name>` (`python -m examples.advanced`).

## Features
These are features that will exist by the first release of apgorm:
 - Fully type-checked
 - 100% code coverage
 - Easy-to-use
 - Migration support

## Limitations
There are some limitations that should be noted:
 - There are limitations on what the name of a column can be. For example, you cannot have a column named `tablename` since that is used to declare the name of the model.
 - `apgorm` only supports PostgreSQL with asyncpg (although I'd be interested to see if anyone wants to fork apgorm for use with another library/database).
 - Doesn't support python migrations. This means that you can't create your own migration file with python code.

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

import asyncio
import shutil
import warnings
from pathlib import Path

import pytest

from tests.database import Database


@pytest.fixture(scope="package")
async def db():
    migrations = Path("tests/migrations")

    db = Database(migrations)
    await db.connect(database="apgorm_testing_database")

    db.create_migrations()
    if await db.must_apply_migrations():
        await db.apply_migrations()
    else:
        warnings.warn(
            "Unabled to test migrations. Please delete "
            "and recreate the `apgorm_test_database` DB."
        )

    for m in db._all_models:
        if m._tablename == "_migrations":
            continue
        await m.delete_query().execute()

    yield db

    await db.cleanup()
    if migrations.exists():
        shutil.rmtree(migrations)


@pytest.fixture(scope="package")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

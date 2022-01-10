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

import pytest

from apgorm import Model
from apgorm.exceptions import ModelNotFound
from apgorm.undefined import UNDEF
from tests.database import Database, User


def _valid_model(model: Model) -> bool:
    all_fields = model.all_fields
    pk_fields = {p.name: p for p in model.primary_key}

    if not all([pkf is all_fields[pkf.name] for pkf in pk_fields.values()]):
        return False

    if not all([f._value is not UNDEF.UNDEF for f in all_fields.values()]):
        return False

    return True


@pytest.mark.asyncio
async def test_model(db: Database) -> None:
    # test basic creation
    names = ["Circuit", "User 5", "Unamed", "James"]
    for n in names:
        user = User(name=n)
        assert not _valid_model(user)
        assert user is await user.create()
        assert _valid_model(user)

    # test fetching
    circuit = await User.fetch(name="Circuit")
    assert _valid_model(circuit)
    assert circuit.name.v == "Circuit"

    assert len(await User.fetch_query().fetchmany()) == 4
    assert len(await User.fetch_query().fetchmany(limit=3)) == 3

    assert (
        len(
            await User.fetch_query().where(User.name.neq("Unamed")).fetchmany()
        )
        == 3
    )

    # test saving
    circuit.nickname.v = "therealcircuit"
    await circuit.save()

    _circuit = await User.fetch(name="Circuit")
    assert _circuit.nickname.v == "therealcircuit"

    # test update query
    all_users = (
        await User.fetch_query().where(User.name.neq("Circuit")).fetchmany()
    )
    assert all([u.nickname.v is None for u in all_users])

    await User.update_query().where(User.name.neq("Circuit")).set(
        nickname="nick"
    ).execute()
    all_users = (
        await User.fetch_query().where(User.name.neq("Circuit")).fetchmany()
    )
    assert all([u.nickname.v == "nick" for u in all_users])

    # test Model.refetch
    orig = await User.fetch(name="Circuit")
    assert orig.nickname.v == "therealcircuit"
    await User.update_query().where(name="Circuit").set(
        nickname="new nick"
    ).execute()
    assert orig.nickname.v == "therealcircuit"
    await orig.refetch()
    assert orig.nickname.v == "new nick"

    # test eq
    assert (await User.fetch(name="Circuit")) == (
        await User.fetch(name="Circuit")
    )

    # test deletion
    circuit = await User.fetch(name="Circuit")
    await circuit.delete()
    try:
        await User.fetch(name="Circuit")
    except ModelNotFound:
        pass
    else:
        raise AssertionError("User wasn't deleted?")

    # test deletion query
    await User.delete_query().execute()
    assert len(await User.fetch_query().fetchmany()) == 0

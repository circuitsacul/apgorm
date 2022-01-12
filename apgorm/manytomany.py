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

from typing import TYPE_CHECKING, Any, Generic, Type, TypeVar, cast

if TYPE_CHECKING:  # pragma: no cover
    from .connection import Connection
    from .field import Field
    from .model import Model
    from .utils.lazy_list import LazyList


_REF = TypeVar("_REF", bound="Model")


class ManyToMany(Generic[_REF]):
    """A useful tool to simplify many-to-many references.

    Args:
        here (str): The field name on the current column.
        here_ref (str): The model and field name on the "middle" table (in the
        example below, the middle table is Player) in the format of
        "model.field".
        other_ref (str): The model and field name on the middle table that
        references the final table (or other table).
        other (str): The model and field name on the final table referenced by
        the middle table.

    Note: Although unecessary, it is highly recommended to use ForeignKeys on
    the middle table where it references the initial and final table. You may
    get unexpected behaviour if you don't.

    Example Usage:
    ```
    class User(Model):
        username = VarChar(32).field()
        primary_key = (username,)

        games = ManyToMany(
            # the column on this table referenced in Player
            "username",

            # the column on Player that references "username"
            "players.username",

            # the column on Player that references Game.gameid
            "players.gameid",

            # the column on Game referenced by Player
            "games.gameid",
        )

    class Game(Model):
        gameid = Serial().field()
        primary_key = (gameid,)

        users = ManyToMany(
            "gameid",
            "players.gameid",
            "players.username",
            "users.username",
        )

    class Player(Model):
        username = VarChar(32).field()
        gameid = Int().field()
        primary_key = (username, gameid)

        username_fk = ForeignKey(username, User.username)
        gameid_fk = ForeignKey(gameid, Game.gameid)

    class MyDatabase(Database):
        users = User
        games = Game
        players = Player

    ...

    circuit = await User.fetch(username="Circuit")
    circuits_games = await circuit.games.fetchmany()
    ```

    If you want typehints to work properly, use
    `games = ManyToMany["Game"](...)`.
    """

    def __init__(
        self,
        here: str,
        here_ref: str,
        other_ref: str,
        other: str,
    ) -> None:
        self.here = here
        self.here_ref = here_ref
        self.other_ref = other_ref
        self.other = other

    async def fetchmany(
        self, con: Connection | None = None
    ) -> LazyList[dict, _REF]:
        """Fetch all rows from the final table that belong to this instance.

        Returns:
            LazyList[dict, Model]: A lazy-list of returned Models.
        """

        raise NotImplementedError  # pragma: no cover

    def _generate_mtm(self, inst: Model) -> ManyToMany:
        # NOTE: see comment under _RealManyToMany
        if TYPE_CHECKING:  # pragma: no cover
            return self
        return _RealManyToMany(self, inst)


class _RealManyToMany:
    # HACK: ManyToMany doesn't store a reference to the model instance, which
    # is necessary in order to properly carry out the query. This was the
    # easiest solution. No type checker will know that the value of the
    # ManyToMany is actually _RealManyToMany when a Model is initialized, so a
    # couple things break (such as __init__). This shouldn't really be a
    # problem since the only user-facing method is fetchmany().
    def __init__(
        self,
        orig: ManyToMany,
        model_inst: Model,
    ) -> None:
        # NOTE: all these casts are ugly, but truthfully
        # there isn't a better way to do this. You can't
        # actually check that these are Models and Fields
        # without creating circular imports (since model.py
        # imports this file)

        self.orig = orig

        mm_h_model, _mm_h_field = self.orig.here_ref.split(".")
        mm_o_model, _mm_o_field = self.orig.other_ref.split(".")
        assert mm_h_model == mm_o_model

        mm_model = cast(
            "Type[Model]", getattr(model_inst.database, mm_h_model)
        )

        mm_h_field = cast("Field", getattr(mm_model, _mm_h_field))
        mm_o_field = cast("Field", getattr(mm_model, _mm_o_field))

        _ot_model, _ot_field = self.orig.other.split(".")
        ot_model = cast("Type[Model]", getattr(model_inst.database, _ot_model))

        ot_field = cast("Field", getattr(ot_model, _ot_field))

        self.model = model_inst
        self.field = cast("Field", getattr(model_inst, self.orig.here))
        self.mm_model = mm_model
        self.mm_h_field = mm_h_field
        self.mm_o_field = mm_o_field
        self.ot_model = ot_model
        self.ot_field = ot_field

    def __getattr__(self, name: str) -> Any:
        return getattr(self.orig, name)

    async def fetchmany(
        self, con: Connection | None = None
    ) -> LazyList[dict, Model]:
        return (
            await self.ot_model.fetch_query(con=con)
            .where(
                self.mm_model.fetch_query()
                .where(
                    self.mm_h_field.eq(self.field.v),
                    self.mm_o_field.eq(self.ot_field),
                )
                .exists()
            )
            .fetchmany()
        )
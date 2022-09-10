from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterable,
    Type,
    TypeVar,
    cast,
    overload,
)

if TYPE_CHECKING:  # pragma: no cover
    from .connection import Connection
    from .field import BaseField
    from .model import Model
    from .utils.lazy_list import LazyList


_REF = TypeVar("_REF", bound="Model")
_THROUGH = TypeVar("_THROUGH", bound="Model")


class ManyToMany(Generic[_REF, _THROUGH]):
    """A useful tool to simplify many-to-many references.

    Args:
        here (str): The field name on the current model.
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

        games = ManyToMany["Game", "Player"](  # the typehints are optional
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

        users = ManyToMany["User", "Player"](
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

    __slots__: Iterable[str] = (
        "_here",
        "_here_ref",
        "_other_ref",
        "_other",
        "_attribute_name",
    )

    _attribute_name: str
    # populated by Model on __init_subclass__

    def __init__(
        self, here: str, here_ref: str, other_ref: str, other: str
    ) -> None:
        self._here = here
        self._here_ref = here_ref
        self._other_ref = other_ref
        self._other = other

    @overload
    def __get__(
        self, inst: Model, cls: Type[Model]
    ) -> _RealManyToMany[_REF, _THROUGH]:
        ...

    @overload
    def __get__(
        self, inst: None, cls: Type[Model]
    ) -> ManyToMany[_REF, _THROUGH]:
        ...

    def __get__(
        self, inst: Model | None, cls: type[Model]
    ) -> ManyToMany[_REF, _THROUGH] | _RealManyToMany[_REF, _THROUGH]:
        if inst is None:
            return self
        real_m2m = self._generate_mtm(inst)
        setattr(inst, self._attribute_name, real_m2m)
        return real_m2m

    def _generate_mtm(self, inst: Model) -> _RealManyToMany[_REF, _THROUGH]:
        return _RealManyToMany(self, inst)


class _RealManyToMany(Generic[_REF, _THROUGH]):
    __slots__: Iterable[str] = (
        "orig",
        "model",
        "field",
        "mm_model",
        "mm_h_field",
        "mm_o_field",
        "ot_model",
        "ot_field",
    )

    def __init__(
        self, orig: ManyToMany[_REF, _THROUGH], model_inst: Model
    ) -> None:
        # NOTE: all these casts are ugly, but truthfully
        # there isn't a better way to do this. You can't
        # actually check that these are Models and Fields
        # without creating circular imports (since model.py
        # imports this file)

        self.orig = orig

        mm_h_model, _mm_h_field = self.orig._here_ref.split(".")
        mm_o_model, _mm_o_field = self.orig._other_ref.split(".")
        assert mm_h_model == mm_o_model

        mm_model = cast(
            "Type[_THROUGH]", getattr(model_inst.database, mm_h_model)
        )

        mm_h_field = cast(
            "BaseField[Any, Any, Any]", getattr(mm_model, _mm_h_field)
        )
        mm_o_field = cast(
            "BaseField[Any, Any, Any]", getattr(mm_model, _mm_o_field)
        )

        _ot_model, _ot_field = self.orig._other.split(".")
        ot_model = cast("Type[_REF]", getattr(model_inst.database, _ot_model))

        ot_field = cast(
            "BaseField[Any, Any, Any]", getattr(ot_model, _ot_field)
        )

        self.model = model_inst
        self.field = cast(
            "BaseField[Any, Any, Any]",
            getattr(model_inst.__class__, self.orig._here),
        )
        self.mm_model = mm_model
        self.mm_h_field = mm_h_field
        self.mm_o_field = mm_o_field
        self.ot_model = ot_model
        self.ot_field = ot_field

    def __getattr__(self, name: str) -> Any:
        return getattr(self.orig, name)

    async def fetchmany(
        self, con: Connection | None = None
    ) -> LazyList[dict[str, Any], _REF]:
        """Fetch all rows from the final table that belong to this instance.

        Returns:
            LazyList[dict, Model]: A lazy-list of returned Models.
        """

        return (
            await self.ot_model.fetch_query(con=con)
            .where(
                self.mm_model.fetch_query()
                .where(
                    self.mm_h_field.eq(
                        self.model._raw_values[self.field.name]
                    ),
                    self.mm_o_field.eq(self.ot_field),
                )
                .exists()
            )
            .fetchmany()
        )

    async def count(self, con: Connection | None = None) -> int:
        """Returns the count.

        Warning: To be efficient, this returns the count of *middle* models,
        which may differ from the number of final models if you did not use
        ForeignKeys properly.

        Returns:
            int: The count.
        """

        return (
            await self.mm_model.fetch_query(con=con)
            .where(self.mm_h_field.eq(self.model._raw_values[self.field.name]))
            .count()
        )

    async def clear(
        self, con: Connection | None = None
    ) -> LazyList[dict[str, Any], _THROUGH]:
        """Remove all instances of the other model from this instance.

        Both of these lines do the same thing:
        ```
        deleted_players = await user.games.clear()
        deleted_players = await Player.delete_query().where(
            username=user.name
        ).execute()
        ```

        Returns:
            LazyList[dict, _THROUGH]: A lazy-list of deleted through models (in
            the example, it would be a list of Player).
        """

        return (
            await self.mm_model.delete_query(con=con)
            .where(self.mm_h_field.eq(self.model._raw_values[self.field.name]))
            .execute()
        )

    async def add(self, other: Model, con: Connection | None = None) -> Model:
        """Add one or more models to this ManyToMany.

        Each of these lines does the exact same thing:
        ```
        player = await user.games.add(game)
        # OR
        player = await games.users.add(user)
        # OR
        player = await Player(username=user.name, gameid=game.id).create()
        ```

        Returns:
            Model: The reference model that lines this model and the other
            model. In the example, the return would be a Player.
        """

        values = {
            self.mm_h_field.name: self.model._raw_values[self.field.name],
            self.mm_o_field.name: other._raw_values[self.ot_field.name],
        }
        return await self.mm_model(**values).create(con=con)

    async def remove(
        self, other: Model, con: Connection | None = None
    ) -> LazyList[dict[str, Any], _THROUGH]:
        """Remove one or models from this ManyToMany.

        Each of these lines does the exact same thing:
        ```
        deleted_players = await user.games.remove(game)
        # OR
        deleted_players = await games.user.remove(user)
        # OR
        deleted_players = await Player.delete_query().where(
            username=user.name, gameid=game.id
        ).execute()
        ```

        Note: The fact that .remove() returns a list instead of a single model
        was intentional. The reason is ManyToMany does not enforce uniqueness
        in any way, so there could be multiple Players that link a single user
        to a single game. Thus, user.remove(game) could actually end up
        deleting multiple players.
        """

        values = {
            self.mm_h_field.name: self.model._raw_values[self.field.name],
            self.mm_o_field.name: other._raw_values[self.ot_field.name],
        }
        return (
            await self.mm_model.delete_query(con=con).where(**values).execute()
        )

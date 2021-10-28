from __future__ import annotations

from typing import TYPE_CHECKING, Any, Type, TypeVar

from apgorm.field import Field
from apgorm.field import field as create_field
from apgorm.sql import DeleteQuery, FetchQuery, InsertQuery, UpdateQuery
from apgorm.types.numeric import Serial
from apgorm.undefined import UNDEF

from .constraints import Constraint

if TYPE_CHECKING:
    from .database import Database


_T = TypeVar("_T", bound="Model")


class Model:
    tablename: str
    database: Database  # populated by Database

    uid = create_field(Serial(), pk=True, read_only=True)

    def __init__(self, **values):
        if "uid" in values:
            self.uid._value = values["uid"]

        self.fields: dict[str, Field[Any, Any]] = {}

        all_fields, _ = self._special_attrs()
        for f in all_fields.values():
            f = f.copy()
            self.fields[f.name] = f
            setattr(self, f.name, f)

            value = values.get(f.name, f.default)
            f._value = value

    async def delete(self):
        await self.delete_query().where(uid=self.uid.value).execute()

    async def save(self):
        changed_fields = self._get_changed_fields()
        q = self.update_query().where(uid=self.uid.value)
        q.set(**{f.name: f.value for f in changed_fields})
        await q.execute()
        self._set_saved()

    async def create(self):
        q = self.insert_query()
        q.set(
            **{
                f.name: f.value
                for f in self.fields.values()
                if f._value is not UNDEF.UNDEF
            }
        )
        uid = await q.execute()
        self.uid._value = uid

    @classmethod
    async def fetch(cls: Type[_T], **values) -> _T:
        res = await cls.fetch_query().where(**values).fetchone()
        if res is None:
            raise Exception("Model not found.")
        return res

    @classmethod
    def fetch_query(cls: Type[_T]) -> FetchQuery[_T]:
        return FetchQuery(model=cls)

    @classmethod
    def delete_query(cls: Type[_T]) -> DeleteQuery[_T]:
        return DeleteQuery(model=cls)

    @classmethod
    def update_query(cls: Type[_T]) -> UpdateQuery[_T]:
        return UpdateQuery(model=cls)

    @classmethod
    def insert_query(cls: Type[_T]) -> InsertQuery[_T]:
        return InsertQuery(model=cls)

    def _set_saved(self):
        for f in self.fields.values():
            f.changed = False

    def _get_changed_fields(self) -> list[Field]:
        fields: list[Field] = []
        for f in self.fields.values():
            if f.changed:
                fields.append(f)
        return fields

    @classmethod
    def _special_attrs(cls) -> tuple[dict[str, Field], dict[str, Constraint]]:
        fields: dict[str, Field] = {}
        constraints: dict[str, Constraint] = {}

        for attr_name in dir(cls):
            try:
                attr = getattr(cls, attr_name)
            except AttributeError:
                continue

            if isinstance(attr, Field):
                fields[attr_name] = attr

            elif isinstance(attr, Constraint):
                constraints[attr_name] = attr

        return fields, constraints

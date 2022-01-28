from __future__ import annotations

from typing import Type, overload


class Getter:
    @overload
    def __get__(self, inst: Thing, cls: Type[Thing]) -> int:
        ...

    @overload
    def __get__(self, inst: None, cls: Type[Thing]) -> Getter:
        ...

    def __get__(self, cls, inst):
        if not inst:
            return self

        return 1


class Thing:
    x = Getter()


Thing.x
Thing().x

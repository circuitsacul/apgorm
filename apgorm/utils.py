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

from typing import TYPE_CHECKING, List, get_type_hints

__all__ = ("nested_dataclass",)


if TYPE_CHECKING:
    from dataclasses import dataclass as nested_dataclass
else:
    from dataclasses import dataclass, is_dataclass

    field_type = None

    def nested_dataclass(*args, **kwargs):
        def wrapper(cls):
            cls = dataclass(cls, **kwargs)
            original_init = cls.__init__

            def __init__(self, *args, **kwargs):
                field_types = get_type_hints(cls)
                for name, value in kwargs.items():
                    field_type = field_types.get(name, None)
                    if isinstance(value, list):
                        if (
                            field_type.__origin__ == List
                            or field_type.__origin__ == list
                        ):
                            sub_type = field_type.__args__[0]
                            if is_dataclass(sub_type):
                                items = []
                                for child in value:
                                    if isinstance(child, dict):
                                        items.append(sub_type(**child))
                                    else:
                                        items.append(child)
                                kwargs[name] = items
                    if is_dataclass(field_type) and isinstance(value, dict):
                        new_obj = field_type(**value)
                        kwargs[name] = new_obj
                original_init(self, *args, **kwargs)

            cls.__init__ = __init__
            return cls

        return wrapper(args[0]) if args else wrapper

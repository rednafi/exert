from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from typing import (
    Annotated,
    Callable,
    Generic,
    Iterable,
    TypeVar,
    cast,
    get_type_hints,
    overload,
    Any
)

if sys.version_info >= (3, 9):
    from typing import _AnnotatedAlias  # type: ignore
else:
    from typing_extensions import _AnnotatedAlias  # type: ignore


_C = TypeVar("_C")
_T = TypeVar("_T")


class _N:
    pass


_NOTHING = _N()


class Convertor(Generic[_T]):
    """Descriptor that applies convertor callables on the attribute values."""

    def __init__(self, *convertors: Callable) -> None:
        self._convertors = convertors
        self._attr = None  # type: str | None
        self._value = None  # type: _T | None

    def __set_name__(self, owner: type[_C], name: str) -> None:
        self._attr = name

    @overload
    def __get__(self, obj: None, objtype: None) -> Convertor:
        ...

    @overload
    def __get__(self, obj: _C, objtype: type[_C]) -> _T:
        ...

    def __get__(self, obj: _C | None, objtype: type[_C] | None) -> Convertor | _T:
        if obj is None:
            return self
        return cast(_T, self._value)

    def __set__(self, obj: object, value: _T) -> None:
        for convertor in self._convertors:
            if not callable(convertor):
                raise TypeError("convertor must be a callable")
            value = convertor(value)
        self._value = value

    def __repr__(self) -> str:
        return "<exert Convertor>"


def exert(
    cls: type[_C] | None = None,
    *,
    exclude: Iterable[str] | None = None,
) -> Callable:

    """Apply the Convertor on the class attributes."""

    def wrapper(cls: type[_C]) -> type[_C]:
        typ_ann = get_type_hints(cls, include_extras=True)
        cls_dict_get = cls.__dict__.get

        for attr, typ in typ_ann.items():
            if isinstance(exclude, Iterable) and attr in exclude:
                continue
            if not (isinstance(typ, _AnnotatedAlias) and cls_dict_get(attr, _NOTHING)):
                continue
            setattr(cls, attr, Convertor(*typ.__metadata__))
        return cls

    if cls is not None:
        return wrapper(cls)

    return wrapper


@exert(exclude=("a",))
@dataclass
class Hello:
    a: Annotated[int, lambda x: x**2]
    b: Annotated[int, lambda x: x**3]
    c: int = 4

    # def __init__(self, a, b):
    #     self.a = a
    #     self.b = b


h = Hello(2, 2)
print(h.b)
# print(h.a)
# print(h.b)
# print(h.c)

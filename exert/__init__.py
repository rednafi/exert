from __future__ import annotations

import sys
from typing import Callable, Generic, Iterable, TypeVar, cast, overload

if sys.version_info >= (3, 9):
    from typing import Annotated, get_args, get_origin, get_type_hints  # type: ignore
else:
    from typing_extensions import (  # type: ignore
        Annotated,
        get_args,
        get_origin,
        get_type_hints,
    )


__all__ = ("exert", "Mark")

_C = TypeVar("_C")
_T = TypeVar("_T")


class Convert(Generic[_T]):
    """Descriptor that applies converter callables to the attribute values."""

    def __init__(self, *converters: Callable) -> None:
        self._converters = converters
        self._attr = None  # type: str | None
        self._value = None  # type: _T | None

    def __set_name__(self, owner: type[_C], name: str) -> None:
        self._attr = name

    @overload
    def __get__(self, obj: None, objtype: None) -> Convert:
        ...

    @overload
    def __get__(self, obj: _C, objtype: type[_C]) -> _T:
        ...

    def __get__(self, obj: _C | None, objtype: type[_C] | None) -> Convert | _T:
        if obj is None:
            return self
        return cast(_T, self._value)

    def __set__(self, obj: object, value: _T) -> None:
        for converter in self._converters:
            if not callable(converter):
                raise TypeError(f"{converter} is not a callable")
            value = converter(value)
        self._value = value

    def __repr__(self) -> str:
        return "<exert Convert>"


class Mark:
    def __init__(self, *converters: Callable) -> None:
        self._converters = converters

    def __repr__(self) -> str:
        return "<exert Converter>"


def get_markers_from_annotation(
    annotation: type, marker_cls: type[Mark]
) -> list[Callable]:
    """
    In the case of multiple markers in PEP 593 Annotated or nested use of
    Annotated (which are equivalent and get flattened by Annoated itself),
    we return markers from left to right.
    """

    return [
        converter
        for arg in get_args(annotation)
        if isinstance(arg, marker_cls)
        for converter in arg._converters
    ]


def exert(
    cls: type[_C] | None = None,
    *,
    converters: Iterable[Callable] | None = None,
    apply_last: bool = False,
) -> Callable:

    """Apply the converters to the class attributes.

    By default, fields with the 'Annotated' type-hints are included
    and the rest are excluded.

    Parameters
    ----------
    cls : type[_C] | None, optional
        Undecorated class, by default None

    converters : Iterable[Callable] | None, optional
        Callables to be applied, by default None

    apply_last : bool, optional
        Apply the converters after everything else, by default

    Returns
    -------
    Callable
        Decorated class
    """

    def wrapper(cls: type[_C]) -> type[_C]:
        typ_ann = get_type_hints(cls, include_extras=True)

        for attr, typ in typ_ann.items():
            if not get_origin(typ) is Annotated:
                continue

            marked_converters = get_markers_from_annotation(typ, Mark)

            if isinstance(converters, Iterable):
                if apply_last and isinstance(converters, Iterable):
                    setattr(cls, attr, Convert(*marked_converters, *converters))
                else:
                    setattr(cls, attr, Convert(*converters, *marked_converters))
            else:
                setattr(cls, attr, Convert(*marked_converters))
        return cls

    if cls is not None:
        return wrapper(cls)
    return wrapper

from __future__ import annotations

import sys
from typing import Callable, Generic, Iterable, TypeVar, cast, overload

if sys.version_info >= (3, 9):
    from typing import _AnnotatedAlias, get_type_hints  # type: ignore
else:
    from typing_extensions import _AnnotatedAlias, get_type_hints  # type: ignore


_C = TypeVar("_C")
_T = TypeVar("_T")


class _N:
    pass


_NOTHING = _N()


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
                raise TypeError("converter must be a callable")

            value = converter(value)
        self._value = value

    def __repr__(self) -> str:
        return "<exert Convert>"


def exert(
    cls: type[_C] | None = None,
    *,
    converters: Iterable[Callable] | None = None,
    apply_last: bool = False,
    tagged_exclude: Iterable[str] | str | None = None,
    untagged_include: Iterable[str] | str | None = None,
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

    tagged_exclude : Iterable[str] | None, optional
        Fields with the 'Annotated' tag to be excluded, by default None

    untagged_include : Iterable[str] | None, optional
        Fields without the 'Annotated' tag to be included, by default None


    Returns
    -------
    Callable
        Decorated class
    """

    def wrapper(cls: type[_C]) -> type[_C]:
        typ_ann = get_type_hints(cls, include_extras=True)
        cls_dict_get = cls.__dict__.get

        untagged_include_error = (
            "field in the 'untagged_include' parameter cannot be tagged "
            "with 'Annotated'"
        )

        tagged_exclude_error = (
            "field in the 'tagged_exclude' parameter must be tagged with 'Annotated'"
        )

        for attr, typ in typ_ann.items():
            if untagged_include == "__all__":
                if isinstance(typ, _AnnotatedAlias):
                    raise TypeError(untagged_include_error)
                if isinstance(converters, Iterable):
                    setattr(cls, attr, Convert(*converters))

            elif isinstance(untagged_include, Iterable) and attr in untagged_include:
                if isinstance(typ, _AnnotatedAlias):
                    raise TypeError(untagged_include_error)
                if isinstance(converters, Iterable):
                    setattr(cls, attr, Convert(*converters))

            if tagged_exclude == "__all__":
                if not isinstance(typ, _AnnotatedAlias):
                    raise TypeError(tagged_exclude_error)
                continue

            elif isinstance(tagged_exclude, Iterable) and attr in tagged_exclude:
                if not isinstance(typ, _AnnotatedAlias):
                    raise TypeError(tagged_exclude_error)
                continue

            if not (isinstance(typ, _AnnotatedAlias) and cls_dict_get(attr, _NOTHING)):
                continue

            if isinstance(converters, Iterable):
                if apply_last and isinstance(converters, Iterable):
                    setattr(cls, attr, Convert(*typ.__metadata__, *converters))
                else:
                    setattr(cls, attr, Convert(*converters, *typ.__metadata__))
            else:
                setattr(cls, attr, Convert(*typ.__metadata__))
        return cls

    if cls is not None:
        return wrapper(cls)

    return wrapper

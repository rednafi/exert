from __future__ import annotations

import json
import sys
from dataclasses import dataclass

import pytest

import exert as main

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (2**2, 3**3)),
        (4, 5, (4**2, 5**3)),
        (6, 7, (6**2, 7**3)),
    ),
)
def test_class_with_one_converter(a, b, expected):
    @main.exert
    class Foo:
        a: Annotated[int, lambda x: x**2]
        b: Annotated[int, lambda x: x**3]

        def __init__(self, a, b):
            self.a = a
            self.b = b

    foo = Foo(a, b)

    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        ({"hello": "world"}, 3, (json.dumps({"hello": "world"}), f"{3**3}__suffix")),
        ({"hello": "mars"}, 5, (json.dumps({"hello": "mars"}), f"{5**3}__suffix")),
    ),
)
def test_class_with_many_converter(a, b, expected):
    @main.exert
    class Foo:
        a: Annotated[dict, json.dumps]
        b: Annotated[int, lambda x: x**3, str, lambda x: x + "__suffix"]

        def __init__(self, a, b):
            self.a = a
            self.b = b

    foo = Foo(a, b)

    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        ({"hello": "world"}, 3, (json.dumps({"hello": "world"}), f"{3**3}__suffix")),
        ({"hello": "mars"}, 5, (json.dumps({"hello": "mars"}), f"{5**3}__suffix")),
    ),
)
def test_dataclass_with_many_converter(a, b, expected):
    @main.exert
    @dataclass
    class Foo:
        a: Annotated[dict, json.dumps]
        b: Annotated[int, lambda x: x**3, str, lambda x: x + "__suffix"]

    foo = Foo(a, b)

    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (str(2**2), str(3**3))),
        (4, 5, (str(4**2), str(5**3))),
    ),
)
def test_dataclass_with_arg_converter(a, b, expected):
    @main.exert(converters=(str,), apply_last=True)
    @dataclass
    class Foo:
        a: Annotated[int, lambda x: x**2]
        b: Annotated[int, lambda x: x**3]

    foo = Foo(a, b)

    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (2, str(3**3))),
        (4, 5, (4, str(5**3))),
    ),
)
def test_dataclass_with_exclude(a, b, expected):
    @main.exert(converters=(str,), apply_last=True, tagged_exclude=("a",))
    @dataclass
    class Foo:
        a: Annotated[int, lambda x: x**2]
        b: Annotated[int, lambda x: x**3]

    foo = Foo(a, b)

    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (str(2**2), str(3))),
        (4, 5, (str(4**2), str(5))),
    ),
)
def test_dataclass_with_include(a, b, expected):
    @main.exert(converters=(str,), apply_last=True, untagged_include=("b",))
    @dataclass
    class Foo:
        a: Annotated[int, lambda x: x**2]
        b: int

    foo = Foo(a, b)
    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (2, str(3))),
        (4, 5, (4, str(5))),
    ),
)
def test_dataclass_without_annotated(a, b, expected):
    @main.exert(converters=(str,), apply_last=False, untagged_include=("b",))
    @dataclass
    class Foo:
        a: int
        b: int

    foo = Foo(a, b)
    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b


@pytest.mark.parametrize(
    "a,b,c,d,expected",
    (
        ({1: 2, 3: 4}, {1: 2, 3: 4}, 2, 3, ("2", {1: 2, 3: 4}, 2, "3")),
        ({1: 2, 3: 4}, {4: 5, 6: 7}, 2, 3, ("2", {4: 5, 6: 7}, 2, "3")),
    ),
)
def test_dataclass_all(a, b, c, d, expected):
    """Test complex behavior."""

    @main.exert(
        converters=(json.dumps,),
        apply_last=True,
        tagged_exclude=("b",),
        untagged_include=("d",),
    )
    @dataclass
    class Foo:
        a: Annotated[dict, lambda d: d[1]]
        b: Annotated[dict, lambda d: d[3]]
        c: int
        d: int

    foo = Foo(a, b, c, d)
    expected_a, expected_b, expected_c, expected_d = expected
    assert foo.a == expected_a
    assert foo.b == expected_b
    assert foo.c == expected_c
    assert foo.d == expected_d

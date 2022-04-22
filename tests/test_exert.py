import json
import sys
from dataclasses import dataclass

import pytest

import exert as main

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


@pytest.fixture
def class_with_one_convertor(a, b):
    @main.exert
    class Foo:
        a: Annotated[int, lambda x: x**2]
        b: Annotated[int, lambda x: x**3]

        def __init__(self, a, b):
            self.a = a
            self.b = b

    yield Foo(a, b)


@pytest.fixture
def class_with_many_convertors(a, b):
    @main.exert
    class Foo:
        a: Annotated[dict, json.dumps]
        b: Annotated[int, lambda x: x**3, str, lambda x: x + "__suffix"]

        def __init__(self, a, b):
            self.a = a
            self.b = b

    yield Foo(a, b)


@pytest.fixture
def dataclass_with_many_convertors(a, b):
    @main.exert
    @dataclass
    class Foo:
        a: Annotated[dict, json.dumps]
        b: Annotated[int, lambda x: x**3, str, lambda x: x + "__suffix"]

    yield Foo(a, b)


@pytest.mark.parametrize(
    "a,b,expected",
    (
        (2, 3, (2**2, 3**3)),
        (4, 5, (4**2, 5**3)),
        (6, 7, (6**2, 7**3)),
    ),
)
def test_class_with_one_converter(class_with_one_convertor, expected):
    foo = class_with_one_convertor
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
def test_class_with_many_converter(class_with_many_convertors, expected):
    foo = class_with_many_convertors
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
def test_dataclass_with_many_converter(dataclass_with_many_convertors, expected):
    foo = dataclass_with_many_convertors
    expected_a, expected_b = expected
    assert foo.a == expected_a
    assert foo.b == expected_b

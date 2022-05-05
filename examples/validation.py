"""Use exert for simple data validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import partial
from typing import Annotated, Sized  # type: ignore

from exert import Mark, exert


def assert_len(x: Sized, length: int) -> Sized:
    """Assert that the incoming attribute has the expected length."""

    assert len(x) == length
    return x


def assert_json(x: dict) -> dict:
    """Assert that the incoming attribute is JSON serializable."""

    try:
        json.dumps(x)
    except TypeError:
        raise AssertionError(f"{x} is not JSON serializable")
    return x


@exert
@dataclass
class Foo:
    a: Annotated[tuple[int, ...], Mark(partial(assert_len, length=3))]
    b: Annotated[dict, Mark(assert_json)]


foo = Foo(a=(1, 2, 3), b={"a": 1, "b": 2})
print(foo)

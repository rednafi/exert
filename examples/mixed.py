"""Mix common and attribute specific converters."""

from __future__ import annotations

import time
from typing import Annotated  # type: ignore

from exert import Mark, exert

t0 = time.time()


@exert(converters=(lambda x: bytes(x),), apply_last=True)
class Foo:
    a: Annotated[int, Mark(lambda x: x**2)]
    b: Annotated[float, Mark(lambda x: x**2, lambda x: x + 3)]
    c: Annotated[int, None]
    d: int

    def __init__(self, a: int, b: float, c: int, d: int) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d


if __name__ == "__main__":
    foo = Foo(2, 3, 4, 5)

    for _ in range(10000000):
        foo.a
        foo.b
        foo.c
        foo.d

    print(time.time() - t0)

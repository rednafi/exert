from __future__ import annotations

from typing import Annotated

from exert import exert


@exert
class Foo:
    a: Annotated[int, lambda x: x**2]
    b: Annotated[float, lambda x: x / 2]

    def __init__(self, a: int, b: float) -> None:
        self.a = a
        self.b = b


foo = Foo(2, 42.0)

from dataclasses import dataclass


@exert(
    converters=(lambda x: x**2, lambda x: x**3),
    untagged_include=("b",),
    apply_last=True,
)
@dataclass
class Foo:
    a: Annotated[int, lambda x: x / 100]
    b: float


foo = Foo(2, 42.0)

print(foo.a)  # prints 6.401e-11   [2/100=0.02, 0.02**2=0.004, 0.0004**3=6.401e-11]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]

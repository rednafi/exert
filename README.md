<h1>Exert<img src='https://user-images.githubusercontent.com/30027932/164949229-8ef0baf9-119c-4cd6-8df9-c1b6644b399b.png' align='right' width='128' height='128'></h1>


<strong>>> <i>Declaratively apply converter functions to class attributes.</i> <<</strong>

</div>

## Installation

Install via pip:

```
pip install exert
```

## Usage

Use this to declaratively apply arbitrary converter functions to the attributes of a
class. For example:

```python
from __future__ import annotations

from typing import Annotated
from exert import exert, Mark


@exert
class Foo:
    a: Annotated[int, Mark(lambda x: x**2)]
    b: Annotated[float, Mark(lambda x: x / 2)]

    def __init__(self, a: int, b: float) -> None:
        self.a = a
        self.b = b


foo = Foo(2, 42.0)

print(foo.a) # prints 4
print(foo.b) # prints 21.0
```

Here, the lambda function tagged with `Mark` is the converter.

### Use with dataclasses

Dataclasses can also be used to avoid writing the initializer by hand. For example:

```python
...

from dataclasses import dataclass


@exert
@datclasses
class Foo:
    a: Annotated[int, Mark(lambda x: x**2)]
    b: Annotated[float, Mark(lambda x: x / 2)]


foo = Foo(2, 42.0)

print(foo.a) # prints 4
print(foo.b) # prints 21.0
```

### Apply multiple converters sequentially

Multiple converters are allowed. For example:

```python
...

@exert
@dataclass
class Foo:
    a: Annotated[int, Mark(lambda x: x**2, lambda x: x**3)]
    b: Annotated[float, Mark(lambda x: x / 2, lambda x: x / 3)]


foo = Foo(2, 42.0)

print(foo.a) # prints 64  [2**2=4, 4**3=64]
print(foo.b) # prints 7.0 [42.0/2=21.0, 21.0/3=7.0]
```

Here, the converters are applied sequentially. The result of the preceding converter is
fed into the succeeding converter as input. You've to make sure that the number of the returned values of the preceding converter matches that of the succeeding converter.

### Exclude annotated fields

If you don't wrap converters with `Mark`, the corresponding field won't be transformed:

```python
...

@exert
@dataclass
class Foo:
    a: Annotated[int, Mark(lambda x: x**2, lambda x: x**3)]
    b: Annotated[float, lambda x: x / 2, lambda x: x / 3]


foo = Foo(2, 42.0)

print(foo.a)  # prints 64  [2**2=4, 4**3=64]
print(foo.b)  # prints 42.0 [This field was ignored]
```

Since the converters in field `b` weren't tagged with `Mark`, no conversion happened.


### Apply common converters without repetition

Common converters can be applied to multiple fields without repetition:

```python
...

@exert(converters=(lambda x: x**2,))
@dataclass
class Foo:
    a: Annotated[int, None]
    b: Annotated[float, None]


foo = Foo(2, 42.0)

print(foo.a)  # prints 4      [2**2=4]
print(foo.b)  # prints 1764.0 [42.0**2=1764.0]
```

### Apply common and marked converters together

You can apply a sequence of common converters and marked converters together. By default,
the common converters are applied first and then the tagged converters are applied
sequentially:

```python
...

@exert(converters=(lambda x: x**2, lambda x: x**3))
@dataclass
class Foo:
    a: Annotated[int, Mark(lambda x: x / 100)]
    b: Annotated[float, None]


foo = Foo(2, 42.0)

print(foo.a)  # prints 0.64         [2**2=4, 4**3=64, 64/100=0.64]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]
```

You can also, choose to apply the common converters after the tagged ones. For this,
you'll need to set the `apply_last` parameter to `True`:

```python
...

@exert(
    converters=(lambda x: x**2, lambda x: x**3),
    apply_last=True,
)
@dataclass
class Foo:
    a: Annotated[int, Mark(lambda x: x / 100)]
    b: Annotated[float, None]


foo = Foo(2, 42.0)

print(foo.a)  # prints 6.401e-11 [2/100=0.02, 0.02**2=0.004, 0.0004**3=6.401e-11]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]
```

<div align="center">
<i> ✨ 🍰 ✨ </i>
</div>

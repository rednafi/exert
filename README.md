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
from exert import exert


@exert
class Foo:
    a: Annotated[int, lambda x: x**2]
    b: Annotated[float, lambda x: x / 2]

    def __init__(self, a: int, b: float) -> None:
        self.a = a
        self.b = b


foo = Foo(2, 42.0)

print(foo.a) # prints 4
print(foo.b) # prints 21.0
```

Here, the lambda function inside the `Annotated` tag is the converter.

### Use with dataclasses

Dataclasses can also be used to avoid writing the initializer by hand. For example:

```python
...

from dataclasses import dataclass


@exert
@datclasses
class Foo:
    a: Annotated[int, lambda x: x**2]
    b: Annotated[float, lambda x: x / 2]


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
    a: Annotated[int, lambda x: x**2, lambda x: x**3]
    b: Annotated[float, lambda x: x / 2, lambda x: x / 3]


foo = Foo(2, 42.0)

print(foo.a) # prints 64  [2**2=4, 4**3=64]
print(foo.b) # prints 7.0 [42.0/2=21.0, 21.0/3=7.0]
```


### Exclude tagged fields

If you want to exclude a field that's tagged with `Annotated`, you can do so using the `tagged_exclude` parameter:

```python
...

@exert(tagged_exclude=("b",))
@dataclass
class Foo:
    a: Annotated[int, lambda x: x**2, lambda x: x**3]
    b: Annotated[float, lambda x: x / 2, lambda x: x / 3]


foo = Foo(2, 42.0)

print(foo.a)  # prints 64  [2**2=4, 4**3=64]
print(foo.b)  # prints 42.0 [This field was ignored]
```

### Include untagged fields

By default, `exert` will ignore fields that aren't tagged with `Annotated`. But you can
still apply converters to those fields. You'll need to use `converters` and `untagged_include` together:

```python
...

@exert(converters=(lambda x: x**2, lambda x: x**3), untagged_include=("b",))
@dataclass
class Foo:
    a: int
    b: float


foo = Foo(2, 42.0)

print(foo.a)  # prints 2            [This field remains untouched]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]

```

### Apply common converters without repetition

Common converters can be applied to multiple fields without introducing any repetition. The last section already shows how to do it:

```python
...

@exert(converters=(lambda x: x**2, ), untagged_include=("a", "b"))
@dataclass
class Foo:
    a: int
    b: float


foo = Foo(2, 42.0)

print(foo.a)  # prints 2      [This field remains untouched]
print(foo.b)  # prints 1764.0 [42.0**2=1764.0]
```

### Apply common and tagged converters together

You can apply a sequence of common converters and tagged converters together. By default,
the common converters are applied first and then the tagged converters are applied
sequentially:

```python
...

@exert(converters=(lambda x: x**2, lambda x: x**3), untagged_include=("b",))
@dataclass
class Foo:
    a: Annotated[int, lambda x: x / 100]
    b: float


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
    untagged_include=("b",),
    apply_last=True,
)
@dataclass
class Foo:
    a: Annotated[int, lambda x: x / 100]
    b: float


foo = Foo(2, 42.0)

print(foo.a)  # prints 6.401e-11 [2/100=0.02, 0.02**2=0.004, 0.0004**3=6.401e-11]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]
```

### Include all untagged fields

To apply converters to all the untagged fields, use `untagged_include="__all__"`:

```python
...

@exert(
    converters=(lambda x: x**2, lambda x: x**3),
    untagged_include="__all__",
)
@dataclass
class Foo:
    a: int
    b: float


foo = Foo(2, 42.0)

print(foo.a)  # prints 64   [2**2=4, 4**4=64]
print(foo.b)  # prints 5489031744.0 [42.0**2=1764, 1764**3=5489031744.0]
```

### Exclude all tagged fields

To ignore all the fields tagged with `Annotated`, use `tagged_exclude="__all__"`:

```python
...

@exert(
    converters=(lambda x: x**2, lambda x: x**3),
    tagged_exclude="__all__",
)
@dataclass
class Foo:
    a: Annotated[int, lambda x: x**2]
    b: Annotated[float, lambda x: x**3]


foo = Foo(2, 42.0)

print(foo.a)  # prints 2   [Untouched]
print(foo.b)  # prints 42.0 [Untouched]
```

<div align="center">
<i> ✨ 🍰 ✨ </i>
</div>

# PyTypeInfo

pytypeinfo is a small package that allows to get information about and check instances of typed objects at runtime. Its main purpose is to extend pythons builtin type checking functionality ([`isinstance()`](https://docs.python.org/3/library/functions.html#isinstance) and [`issubclass()`](https://docs.python.org/3/library/functions.html#issubclass)) to also check instance members. It is a wrapper around the [`get_type_hints()`](https://docs.python.org/3/library/typing.html#typing.get_type_hints) function from the python standard library module typing to inspect typed class definitions.

It provides two major classes:

`TypeInfo` contains information about a typed member

`TypeInfoCollection` is collection of TypeInfo instances. The collection can be created from a class.

## Example - Checking instances against typed class definitions

```python
from __future__ import annotations

from typing import NamedTuple

from pytypeinfo import TypeInfoCollection


# Simple typed class definition
class MyConfig(NamedTuple):
    first_value: int = 0
    other_value: str = 'Hello World'

# type information collection
info = TypeInfoCollection(MyConfig)

good_config = MyConfig(value=5, other_value='FooBar')
info.check(good_config)
>>> True

bad_config = MyConfig(value=5.5)
info.check(bad_config)
>>> False
```

## Example - Inspecting type hints

```python
from __future__ import annotations

from typing import NamedTuple

from pytypeinfo import TypeInfoCollection


class MyTypedClass:

    value: Any
    items: tuple[int, ...]
    callback: Callable[[int], bool]


info = TypeInfoCollection(MyTypedClass)

# Get TypeInfo object for member 'value'
info_value = info['value']
info_value.is_any
>>> True


# Get TypInfo object for member 'items' and inspect tuple properties
info_items = info['items']

# Is a tuple and a sequence
info_items.is_tuple
>>> True
info_items.is_sequence
>>> True

# First parameter of tuple generic is an int
info_items.sub_types[0].type is int
>>> True

# Second parameter of tuple generic is ellipsis
info_items.sub_types[1].is_ellipsis
>>> True


# Get TypeInfo object for member 'callback'
info_callback = info['callback']

# callback is callable
info_callback.is_callable
>>> True

# First parameter of callback should be int
info_callback.call_params[0].type is int
>>> True

# Return parameter of callback is bool
info_callback.call_returns.type is bool
>>> True
```
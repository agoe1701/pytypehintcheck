from __future__ import annotations

import sys


if sys.version_info < (3, 9):
    from typing_extensions import Annotated, get_type_hints
else:
    # Import everything that has been introduced in python 3.9
    from typing import Annotated, get_type_hints

if sys.version_info < (3, 10):
    from typing_extensions import TypeAlias, TypeGuard
    NoneType = type(None)
    UnionType = type(None)
else:
    # Import everything that has been introduced in python 3.10
    from types import NoneType, UnionType
    from typing import TypeAlias, TypeGuard

if sys.version_info < (3, 11):
    from typing_extensions import dataclass_transform
else:
    # Import everything that has been introduced in python 3.11
    from typing import dataclass_transform


__all__ = [
    'Annotated',
    'NoneType',
    'TypeAlias',
    'TypeGuard',
    'UnionType',
    'dataclass_transform',
    'get_type_hints',
]

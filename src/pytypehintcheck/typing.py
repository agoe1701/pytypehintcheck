from __future__ import annotations

import sys
from inspect import Parameter, Signature
from typing import (
    Any,
    Callable,
    Mapping,
    NamedTuple,
    Sequence,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)


if sys.version_info < (3, 9):
    from typing_extensions import Annotated, get_type_hints
else:
    # Import everything that has been introduced in python 3.9
    from typing import Annotated, get_type_hints

if sys.version_info < (3, 10):
    from typing_extensions import Concatenate, ParamSpec, TypeAlias, TypeGuard
    NoneType = type(None)
else:
    # Import everything that has been introduced in python 3.10
    from types import NoneType      # noqa
    from typing import Concatenate, ParamSpec, TypeAlias, TypeGuard

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
    'check_signature_types',
    'dataclass_transform',
    'get_type_hints',
    'withSignatureFrom',
]


_PARAMS = ParamSpec("_PARAMS")
_RETURN = TypeVar("_RETURN")


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

_PARAM = (Parameter.KEYWORD_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
_ANN_STR = '__annotations__'


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class SignatureDelta(NamedTuple):
    message: str
    delta: dict[int, tuple[str, str]]


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


def get_annotations(cls: Type, create: bool = False) -> dict[str, str]:
    ann = getattr(cls, _ANN_STR, None)
    if ann is None:
        ann = {}
        if create:
            setattr(cls, _ANN_STR, ann)
    return ann


def has_sequence_type(v: Any) -> bool:  # noqa: ANN401
    return not isinstance(v, (str, bytes)) and isinstance(v, Sequence)


def has_nested_type(v: Any) -> bool:  # noqa: ANN401
    return has_sequence_type(v) or isinstance(v, Mapping)


def withSignatureFrom(f: Callable[Concatenate[Any, _PARAMS], _RETURN], /) -> Callable[[Callable[Concatenate[Any, _PARAMS], _RETURN]], Callable[Concatenate[Any, _PARAMS], _RETURN]]:        # noqa
    return lambda _: _


def parse_types(types: list[Type]) -> list:
    result = []
    for t in types:
        org = get_origin(t)
        if org == Union:
            result += parse_types(get_args(t))
        elif org is tuple:
            result.append(parse_types(get_args(t)))
        else:
            result.append(t)
    return result


def check_signature_types(
    callback: Callable,
    types: tuple
) -> tuple[bool, SignatureDelta]:
    """
    Check a callable signature against a list of expected types.

    :param callback:            Callable to check
    :param types:               Sequence of expected types

    :return:                    Tuple:
                                > [0] = Flag: If True signature types match
                                > [1] = SignatureDelta instance with mismatch
                                >       information

    TODO: More testing
    """
    delta = None
    hints = get_type_hints(callback)
    if tuple(types) == tuple(hints.values()):
        # exact match
        return (True, delta)

    delta_dict = {}
    types_len = len(types)
    params = Signature.from_callable(callback).parameters
    match = True
    i = 0
    for i, v in enumerate(params.values()):
        if i >= types_len:
            # Callback has too many params
            return (False, SignatureDelta('Too many arguments', {}))

        if v.kind == Parameter.VAR_POSITIONAL and match:
            # Accepts all position argument (*arg)
            return (True, None)

        if v.kind in _PARAM:
            if v.annotation == Parameter.empty:
                # Parameter type not specified. Considered a match
                continue
            if types[i].__name__ == v.annotation:
                # Parameter type name matches
                continue

            delta_dict[i + 1] = (types[i].__name__, v.annotation)
            match = False

    if match and ((i + 1) < types_len):
        match = False
        delta = SignatureDelta('Too few arguments', {})
    else:
        delta = SignatureDelta('Invalid parameter type', delta_dict)
    return (match, delta)

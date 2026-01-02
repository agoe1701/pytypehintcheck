from __future__ import annotations

import sys
from collections.abc import Callable
from typing import (
    Any,
    ClassVar,
    Literal,
    Mapping,
    NoReturn,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    _GenericAlias,
    get_args,
    get_origin,
    get_type_hints,
)

from pytypehintcheck.typing import Annotated, NoneType


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------

_HINT_TYPE = Any


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

if sys.version_info < (3, 9):
    def _is_annotation(hint: Any) -> bool:  # noqa: ANN401
        meta = getattr(hint, '__metadata__', None)
        return isinstance(meta, Sequence) and len(meta) > 0

else:
    def _is_annotation(hint: Any) -> bool:  # noqa: ANN401
        return get_origin(hint) is Annotated


def _resolve_hint(hint: _HINT_TYPE) -> Tuple[Type, Tuple[TypeInfo, ...]]:
    sub_types = []
    for arg in get_args(hint):
        if isinstance(arg, (type, _GenericAlias)) or arg is Ellipsis:
            sub_types.append(TypeInfo(arg))
    return tuple(sub_types)


def _raise_type_error(
    required_name: str,
    required_type: Type,
    obj: Any            # noqa: ANN401
) -> NoReturn:
    msg = (
        f'Invalid type: {required_name} must be {required_type.__name__!r} but'
        f' is {type(obj).__name__!r}'
    )
    raise TypeError(msg)


def _raise_length_error(
    expect_len: int,
    actual_len: int,
    name: str
) -> NoReturn:
    name = (' ' + name).strip()
    msg = (
        f'Invalid length:{name} length is {actual_len} '
        f'but must be {expect_len}'
    )
    raise ValueError(msg)


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class TypeInfo:
    __slots__ = (
        'callParams',
        'callReturn',
        'isAnnotation',
        'isCallable',
        'isClassVar',
        'isEllipsis',
        'isLiteral',
        'isMapping',
        'isNone',
        'isSequence',
        'isTuple',
        'isType',
        'isTypeVar',
        'isUnion',
        'literalValues',
        'metadata',
        'origin',
        'subTypes',
        'type'
    )


    def _repr(self, with_prefix: bool = True) -> str:
        result = f'{self.__class__.__name__}: ' if with_prefix else ''

        if self.isTypeVar:
            result += 'TypeVar'
            if self.type is not None:
                result += f'[{TypeInfo(self.type)._repr(False)}]'
            return result

        if self.type is None:
            if self.isEllipsis:
                result += '...'
            elif self.isNone:
                result += 'None'
            elif self.isLiteral:
                lt = ', '.join(repr(v) for v in self.literalValues)
                result += f'Literal[{lt}]'

            # TODO: what else can this be?
            return result

        sub_types = None
        if len(self.subTypes):
            sub_types = ', '.join((st._repr(False) for st in self.subTypes))

        if self.isUnion:
            return result + f'Union[{sub_types}]'

        result += self.type.__name__
        if sub_types is not None:
            result += f'[{sub_types}]'

        if self.isCallable:
            params = ', '.join((p._repr(False) for p in self.callParams))
            ret_type = self.callReturn._repr(False)
            result += f'[[{params}], {ret_type}]'

        return result


    def __repr__(self) -> str:
        return self._repr()


    def __eq__(self, other: TypeInfo) -> bool:
        if not isinstance(other, TypeInfo):
            return False

        for attr in TypeInfo.__slots__:
            if getattr(self, attr) != getattr(other, attr):
                return False

        for st_me, st_o in zip(self.subTypes, other.subTypes):
            if st_me != st_o:
                return False

        return True


    def __hash__(self) -> int:
        # TODO: calculate proper hash
        return 0


    def _slot_init(self, hint: _HINT_TYPE) -> NoReturn:
        self.type: TypeVar | tuple[TypeVar, ...] = None
        self.origin: TypeVar = None
        self.subTypes: tuple[TypeInfo, ...] = ()
        self.isType = False
        self.isMapping = False
        self.isSequence = False
        self.isTuple = False
        self.isNone = hint is NoneType or hint is None
        self.isEllipsis = hint is Ellipsis
        self.isAnnotation = False
        self.isClassVar = False
        self.isTypeVar = False
        self.isUnion = False
        self.isLiteral = False
        self.literalValues: tuple[Any, ...] = ()
        self.isCallable = False
        self.callParams: tuple[TypeInfo, ...] = ()
        self.callReturn: TypeInfo = None
        self.metadata: tuple[Any, ...] = ()


    def __init__(self, hint: _HINT_TYPE) -> None:
        self._slot_init(hint)
        if self.isNone or self.isEllipsis:
            return

        self.origin = get_origin(hint)
        self.isType = self.origin is type
        self.isClassVar = self.origin is ClassVar
        self.isLiteral = self.origin is Literal
        self.isTypeVar = isinstance(hint, TypeVar)
        self.isAnnotation = _is_annotation(hint)

        if self.isAnnotation or self.isClassVar:
            self.metadata = getattr(hint, '__metadata__', (None, None))
            args = get_args(hint)
            if args != ():
                self.origin = None
                hint = args[0]

        elif self.isLiteral:
            self.literalValues = get_args(hint)


        elif self.isType:
            self.type = type
            self.subTypes = tuple((TypeInfo(a) for a in get_args(hint)))

        elif self.isTypeVar:
            hint = hint.__bound__
            if hint is None:
                return

        self.isUnion = self.origin is Union
        if self.isUnion:
            _types = []
            sub_types = []
            for arg in get_args(hint):
                _types.append(get_origin(arg) or arg)
                sub_types.append(TypeInfo(arg))

            self.type = tuple(_types)
            self.subTypes = tuple(sub_types)
            return

        self.isCallable = self.origin is Callable
        if self.isCallable:
            self.type = self.origin
            param, return_type = get_args(hint)
            if not isinstance(param, Sequence):
                param = (param,)
            self.callParams = tuple([TypeInfo(a) for a in param])
            self.callReturn = TypeInfo(return_type)
            return

        self.type = self.origin or hint
        self.isTuple = self.origin is tuple
        if self.origin is not None:
            self.isMapping = issubclass(self.origin, Mapping)
            self.isSequence = issubclass(self.origin, Sequence)
        self.subTypes = _resolve_hint(hint)


    def _union_check(
        self,
        obj: Any,  # noqa: ANN401
        name: str,
        do_raise: bool = False
    ) -> bool:
        for ti in self.subTypes:
            if ti._check_instance(obj, name, do_raise):
                return True
        return False


    def _tuple_heck(
        self,
        obj: Any,  # noqa: ANN401
        name: str,
        do_raise: bool = False
    ) -> bool:
        _type = self.subTypes[0]
        num_sub_types = len(self.subTypes)
        if _type.isEllipsis:
            # tuple[...] -> Variable length and any type allowed
            return True

        if num_sub_types == 2 and self.subTypes[1].isEllipsis:  # noqa: PLR2004
            # for example tuple[int, ...]
            return self._sequence_check(obj, name, do_raise)


        if len(self.subTypes) != len(obj):
            if do_raise:
                _raise_length_error(len(self.subTypes), len(obj), name)
            return False

        for index, (tpl_type, obj_item) in enumerate(zip(self.subTypes, obj)):
            if not tpl_type.check(obj_item, f'{name}[{index}]', do_raise):
                return False

        return True


    def _sequence_check(
        self,
        obj: Sequence,
        name: str,
        do_raise: bool = False
    ) -> bool:
        value_type = self.subTypes[0]
        for index, value in enumerate(obj):
            if not value_type.check(
                value,
                f'{name}[{index}]',
                do_raise=do_raise
            ):
                return False
        return True


    def _mapping_check(
        self,
        obj: Mapping,
        name: str,
        do_raise: bool = False
    ) -> bool:
        key_type, value_type = self.subTypes
        for key, value in obj.items():
            if not key_type.check(key, name):
                if do_raise:
                    ...
                return False
            if not value_type.check(
                value,
                f'{name}[{key}]',
                do_raise=do_raise
            ):
                return False
        return True


    def _callable_check(
        self,
        obj: Callable,
        name: str,          # noqa  TODO: raise error with callable name
        do_raise: bool = False
    ) -> bool:
        hints = get_type_hints(obj)
        call_return = TypeInfo(hints.pop('return', None))
        call_params = tuple((TypeInfo(p) for p in hints.values()))

        if len(self.callParams) > 0 and self.callParams[0].isEllipsis:
            return self.callReturn == call_return

        if self.callReturn == call_return and \
           self.callParams == call_params:
            return True

        if do_raise:
            ...

        return False


    def _check_instance(  # noqa: PLR0911, PLR0912  TODO: simplify code
        self,
        obj: Any,  # noqa: ANN401
        name: str,
        do_raise: bool = False
    ) -> bool:
        if self.isUnion:
            return self._union_check(obj, name, do_raise)

        if self.isLiteral:
            if obj not in self.literalValues:
                if do_raise:
                    # TODO: raise exception
                    ...
                return False
            return True

        if not isinstance(obj, self.type):
            if do_raise:
                _raise_type_error(name, self.type, obj)
            return False

        if self.isCallable:
            return self._callable_check(obj, name, do_raise)

        if len(self.subTypes) == 0:
            # Basic instance checked passed, we don't have any subtype so we'r
            # done.
            return True

        if self.isType:
            if not issubclass(obj, self.subTypes):
                if do_raise:
                    ...
                return False
            return True

        if self.isTuple:
            return self._tuple_heck(obj, name, do_raise)

        if self.isMapping:
            return self._mapping_check(obj, name, do_raise)

        if self.isSequence:
            return self._sequence_check(obj, name, do_raise)

        return False


    def _check_class(self, cls: Type) -> bool:
        # TODO: implement further
        return issubclass(cls, self.type)


    def check(
        self,
        obj: Any,  # noqa: ANN401
        name: str = '',
        do_raise: bool = False
    ) -> bool:
        if isinstance(obj, type):
            return self._checkClass(obj, name, doRaise=do_raise)

        return self._check_instance(obj, name, do_raise=do_raise)

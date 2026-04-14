from __future__ import annotations

from typing import Generic, TypeVar, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------

T = TypeVar('T')


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _CustomType:
    ...


class _GenericType(Generic[T]):

    def __init__(self, a: T) -> None:
        self._a = a

    def get(self) -> T:
        return self._a


class _TypeHints:
    foo: bool
    integer: int
    custom: _CustomType
    generic: _GenericType[int]
    tuple: tuple[int, ...]


class TypeTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_TypeHints, include_extras=True)
        return super().setUp()

    def assert_is_type(
        self,
        tp: TypeInfo,
        sub_types: tuple | bool = ()
    ):
        self.assert_type_info(
            tp,
            is_type=True,
            type=tp.type is not None,
            sub_types=sub_types
        )

    def test_simple_type(self):
        info = TypeInfo(self._hints['foo'])

        self.assert_is_type(info)
        assert info.type is bool

    def test_custom_type(self):
        info = TypeInfo(self._hints['custom'])

        self.assert_is_type(info)
        assert info.type is _CustomType

    def test_generic_type(self):
        info = TypeInfo(self._hints['generic'])

        self.assert_is_type(info, sub_types=info.sub_types is not None)
        assert info.type is _GenericType

        t = _GenericType[int](4)
        assert info.check(t)

        assert len(info.sub_types) == 1
        assert info.sub_types[0].type is int

    def test_tuple_type(self):
        info = TypeInfo(self._hints['tuple'])

        assert info.is_type
        assert info.type is tuple
        assert info.is_sequence
        assert info.is_tuple
        assert info.check((1, 2, 3))


if __name__ == '__main__':
    from unittest import main
    main()

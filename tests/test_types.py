from __future__ import annotations

from typing import Type, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------


class _CustomType:
    ...


class _CustomDerived(_CustomType):
    ...


class _TypeHints:
    simple: type
    custom: type[_CustomType]
    derived: type[_CustomDerived]
    deprecated: Type[_CustomType]


class TestTypes(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_TypeHints, include_extras=True)

    def assert_is_type(
        self,
        tp: TypeInfo,
        is_any: bool = False,
        sub_types: tuple | bool = ()
    ):
        self.assert_type_info(
            tp,
            is_any=is_any,
            is_class=True,
            is_type=True,
            type=tp.type is type,
            sub_types=sub_types
        )

    def test_simple_type(self):
        info = TypeInfo(self._hints['simple'])

        self.assert_is_type(info, is_any=True)
        assert info.check(int)
        self.assertRaises(TypeError, info.check, 5, do_raise=True)
        assert not info.check(5)

    def test_custom_types(self):
        info = TypeInfo(self._hints['custom'])

        self.assert_is_type(info, sub_types=info.sub_types != ())
        assert info.sub_types[0].type is _CustomType
        assert info.check(_CustomType)
        assert info.check(_CustomDerived)
        assert not info.check(int)
        assert not info.check(_CustomType())

    def test_derived_type(self):
        info = TypeInfo(self._hints['derived'])

        self.assert_is_type(info, sub_types=info.sub_types != ())
        assert info.sub_types[0].type is _CustomDerived

    def test_deprecated_type(self):
        info = TypeInfo(self._hints['deprecated'])

        self.assert_is_type(info, sub_types=info.sub_types != ())
        assert info.sub_types[0].type is _CustomType


if __name__ == '__main__':
    from unittest import main
    main()

from __future__ import annotations

from typing import Generic, TypeVar, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------

_T = TypeVar('_T')
_TB = TypeVar('_TB', bound=str)
_TS = TypeVar('_TS', str, bytes)


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _TypeVarHints(Generic[_T, _TB, _TS]):
    simple: _T
    bound: _TB
    strict: _TS


class TypeVarTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_TypeVarHints, include_extras=True)
        return super().setUp()

    def assert_is_type_var(
        self,
        tp: TypeInfo,
        is_strict: bool = False,
        sub_types: tuple | bool = ()
    ):
        self.assert_type_info(
            tp,
            is_type_var=True,
            is_strict=is_strict,
            sub_types=sub_types
        )

    def test_type_var_simple(self):
        info = TypeInfo(self._hints['simple'])
        self.assert_is_type_var(info)

    def test_type_var_bound(self):
        info = TypeInfo(self._hints['bound'])
        self.assert_is_type_var(
            info,
            sub_types=info.sub_types != ()
        )

    def test_type_var_strict(self):
        info = TypeInfo(self._hints['strict'])
        self.assert_is_type_var(
            info,
            is_strict=True,
            sub_types=info.sub_types != ()
        )


if __name__ == '__main__':
    from unittest import main
    main()

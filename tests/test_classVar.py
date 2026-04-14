from __future__ import annotations

from typing import ClassVar

import unittest
import sys

from pytypeinfo import TypeInfo
from pytypeinfo.typing import get_type_hints
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

if sys.version_info < (3, 11):
    class _ClassVarHints:
        cl_float: ClassVar[float]
        cl_complex: ClassVar[tuple[int, ...]]
else:
    class _ClassVarHints:
        simple: ClassVar
        cl_float: ClassVar[float]
        cl_complex: ClassVar[tuple[int, ...]]


class ClassVarTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_ClassVarHints, include_extras=True)
        return super().setUp()

    def assert_is_class_var(self, tp: TypeInfo):
        self.assert_type_info(
            tp,
            is_type=True,
            is_class_var=True,
            type=tp.type is not None
        )

    @unittest.skipIf(
        sys.version_info < (3, 11),
        'Plain ClassVar is not supported'
    )
    def test_class_var_simple(self):
        info = TypeInfo(self._hints['simple'])

        assert info.is_class_var
        assert info.is_any

    def test_class_var_generic(self):
        info = TypeInfo(self._hints['cl_float'])

        self.assert_is_class_var(info)
        assert info.type is float
        assert info.check(5.5)
        assert not info.check(5)

    def test_class_var_complex(self):
        info = TypeInfo(self._hints['cl_complex'])

        assert info.is_class_var
        assert info.is_tuple
        assert info.sub_types is not None
        assert len(info.sub_types) == 2

        assert info.check((1, 2, 3, 4))
        assert not info.check((1, 2, '3', 4))


if __name__ == '__main__':
    from unittest import main
    main()

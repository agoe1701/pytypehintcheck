from __future__ import annotations

from typing import Union, get_type_hints

import sys
import unittest

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

if sys.version_info < (3, 10):
    class _UnionHints:
        old: Union[int, str]
else:
    class _UnionHints:
        simple: int | str
        old: Union[int, str]


class UnionTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_UnionHints, include_extras=True)
        return super().setUp()

    def assert_is_union(self, tp: TypeInfo):
        self.assert_type_info(
            tp,
            is_union=True,
            is_type=True,
            type=tp.type is not None,
            sub_types=tp.sub_types is not None
        )

    @unittest.skipIf(
        sys.version_info < (3,10),
        'Not supported in 3.9 and lower'
    )
    def test_simple_union(self):
        info = TypeInfo(self._hints['simple'])

        self.assert_is_union(info)
        assert info.check(5)
        assert info.check('hallo')
        assert not info.check(b'lala')

    def test_legacy_union(self):
        info = TypeInfo(self._hints['old'])

        self.assert_is_union(info)
        assert info.check(5)
        assert info.check('hallo')
        assert not info.check(b'lala')


if __name__ == '__main__':
    from unittest import main
    main()

from __future__ import annotations

from typing import Annotated, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------

Column = Annotated[bool, 'this', 'is', 'a', 'flag']


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _AnnotatedHints:
    simple: Annotated[int, 'some', 'metadata']
    custom: Column


class AnnotatedTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_AnnotatedHints, include_extras=True)
        return super().setUp()

    def assert_is_annotated(self, tp: TypeInfo):
        self.assert_type_info(
            tp,
            is_annotation=True,
            is_type=True,
            type=tp.type is not None,
            metadata=tp.metadata != ()
        )

    def test_annotated_simple(self):
        info = TypeInfo(self._hints['simple'])

        self.assert_is_annotated(info)
        assert info.type is int
        assert info.metadata == ('some', 'metadata')

        assert info.check(5)
        assert not info.check('lala')

    def test_annotated_custom(self):
        info = TypeInfo(self._hints['custom'])

        self.assert_is_annotated(info)
        assert info.type is bool
        assert info.metadata == ('this', 'is', 'a', 'flag')

        assert info.check(True)
        assert not info.check(5.5)


if __name__ == '__main__':
    from unittest import main
    main()

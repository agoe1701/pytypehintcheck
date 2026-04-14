from __future__ import annotations

from typing import Literal, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _LiteralHints:
    simple: Literal[1]
    multiple: Literal[1, 2, 3, 4]
    nested: Literal[1, 2, Literal[3, 4]]        # noqa


class LiteralTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_LiteralHints, include_extras=True)
        return super().setUp()

    def assert_is_literal(self, tp: TypeInfo):
        self.assert_type_info(
            tp,
            is_literal=True,
            literal_values=len(tp.literal_values) > 0,
            origin=tp.origin is Literal
        )

    def test_plain_literal(self):
        info = TypeInfo(self._hints['simple'])

        self.assert_is_literal(info)
        assert info.literal_values[0] == 1

    def test_multiple_literal(self):
        info = TypeInfo(self._hints['multiple'])

        self.assert_is_literal(info)
        assert info.literal_values == (1, 2, 3, 4)

    def test_nested_literal(self):
        # Nested literals will be flattened
        info = TypeInfo(self._hints['nested'])

        self.assert_is_literal(info)
        assert info.literal_values[0] == 1


if __name__ == '__main__':
    from unittest import main
    main()

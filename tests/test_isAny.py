from __future__ import annotations

from typing import Any, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _AnyHints:
    foo: Any
    tuple_of_any: tuple[Any, ...]
    dict_of_any: dict[Any, Any]


class AnyTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_AnyHints, include_extras=True)
        return super().setUp()

    def assert_is_any(self, tp: TypeInfo):
        self.assert_type_info(tp, is_any=True)

    def test_plain_any(self):
        info = TypeInfo(self._hints['foo'])

        self.assert_is_any(info)
        assert info.check(5)
        assert info.check(None)

    def test_tuple_any(self):
        info = TypeInfo(self._hints['tuple_of_any'])

        assert info.sub_types[0].is_any
        assert info.check((1, 2, 3, 4))
        assert info.check(())

    def test_dict_any(self):
        info = TypeInfo(self._hints['dict_of_any'])

        assert info.sub_types[0].is_any
        assert info.sub_types[1].is_any
        assert info.check({})
        assert info.check({'hallo': 'welt'})


if __name__ == '__main__':
    from unittest import main
    main()

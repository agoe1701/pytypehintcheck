from __future__ import annotations

from types import MappingProxyType
from typing import Mapping, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _DictHints:
    plain: dict
    simple: dict[str, int]
    complex: dict[str, tuple[int, ...]]
    immutable: Mapping[str, int]


class MappingTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_DictHints, include_extras=True)
        return super().setUp()

    def assert_is_mapping(
        self,
        tp: TypeInfo,
        is_immutable: bool = False,
        sub_types: tuple | bool = ()
    ):
        self.assert_type_info(
            tp,
            is_mapping=True,
            is_type=True,
            is_immutable=is_immutable,
            type=tp.type is not None,
            sub_types=sub_types
        )

    def test_plain_dict(self):
        info = TypeInfo(self._hints['plain'])
        self.assert_is_mapping(info)

    def test_simple_mapping(self):
        info = TypeInfo(self._hints['simple'])

        self.assert_is_mapping(info, sub_types=info.sub_types is not None)

        assert len(info.sub_types) == 2
        assert info.sub_types[0].type is str
        assert info.sub_types[1].type is int

    def test_complex_mapping(self):
        info = TypeInfo(self._hints['complex'])

        self.assert_is_mapping(info, sub_types=info.sub_types is not None)

        assert info.sub_types is not None
        assert len(info.sub_types) == 2
        assert info.sub_types[0].type is str
        assert info.sub_types[1].type is tuple

    def test_immutable_mapping(self):
        info = TypeInfo(self._hints['immutable'])

        self.assert_is_mapping(
            info,
            sub_types=info.sub_types is not None,
            is_immutable=True
        )

        assert len(info.sub_types) == 2
        assert info.sub_types[0].type is str
        assert info.sub_types[1].type is int

        assert info.check(MappingProxyType({
            'hallo': 1,
            'welt': 2
        }))


if __name__ == '__main__':
    from unittest import main
    main()

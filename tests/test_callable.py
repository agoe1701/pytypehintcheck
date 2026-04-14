from __future__ import annotations

import collections.abc
import typing
from typing import Callable, get_type_hints

from pytypeinfo import TypeInfo
from tests.test_common import TestCommon


# -----------------------------------------------------------------------------
# Types
# -----------------------------------------------------------------------------

_CALLABLE_ABC = collections.abc.Callable
_CALLABLE_TYPING = typing.Callable


# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

def good(a: int, b: str) -> bool:
    ...


def good_empty():
    ...


def good_some_args(a: bool, b: float) -> None:
    ...


def bad_invalid_type(a: float, b: str) -> bool:
    ...


def bad_too_many_params(a: int, b: str, c: float) -> bool:
    ...


def bad_too_few_params(a: int) -> bool:
    ...


def bad_missing_hints(a: int, b) -> bool:       # noqa
    ...


def bad_invalid_return(a: int, b: str) -> float:
    ...


def bad_no_params_no_return() -> None:
    ...


# -----------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------

class _CallableHints:
    call_simple: Callable[[int, str], bool]
    call_ellipsis: Callable[..., bool]
    call_return_none: Callable[..., None]
    call_no_params: Callable[[], None]


class CallableTests(TestCommon):

    def setUp(self) -> None:
        self._hints = get_type_hints(_CallableHints, include_extras=True)
        return super().setUp()

    def assert_is_callable(
        self,
        tp: TypeInfo,
        call_params: bool | tuple,
        call_returns: bool | TypeInfo
    ):
        self.assert_type_info(
            tp,
            is_callable=True,
            call_params=call_params,
            call_returns=call_returns,
            is_type=True,
            type=tp.type in (_CALLABLE_ABC, _CALLABLE_TYPING)
        )

    def test_params_and_return_value(self):
        info = TypeInfo(self._hints['call_simple'])

        self.assert_is_callable(
            info,
            call_params=len(info.call_params) == 2,
            call_returns=info.call_returns is not None
        )
        assert info.call_params[0].type is int
        assert info.call_params[1].type is str
        assert info.call_returns.type is bool

        assert info.check(good)
        assert not info.check(bad_invalid_type)
        assert not info.check(bad_too_many_params)
        assert not info.check(bad_too_few_params)
        assert not info.check(bad_missing_hints)
        assert not info.check(bad_invalid_return)

    def test_variable_params_return_value(self):
        info = TypeInfo(self._hints['call_ellipsis'])

        self.assert_is_callable(
            info,
            call_params=len(info.call_params) == 1,
            call_returns=info.call_returns is not None
        )
        assert info.call_params[0].is_ellipsis
        assert info.call_returns is not None
        assert info.call_returns.type is bool

        assert info.check(good)
        assert not info.check(bad_invalid_return)
        assert not info.check(bad_no_params_no_return)

    def test_no_return(self):
        info = TypeInfo(self._hints['call_return_none'])

        self.assert_is_callable(
            info,
            call_params=len(info.call_params) == 1,
            call_returns=info.call_returns.is_none
        )
        assert len(info.call_params) == 1
        assert info.call_params[0].is_ellipsis

        assert info.check(good_empty)
        assert info.check(good_some_args)
        assert not info.check(good)

    def test_no_params_no_return(self):
        info = TypeInfo(self._hints['call_no_params'])

        self.assert_is_callable(
            info,
            call_params=len(info.call_params) == 0,
            call_returns=info.call_returns.is_none
        )
        assert info.check(good_empty)
        assert info.check(bad_no_params_no_return)
        assert not info.check(good)

    def test_invalid_check(self):
        info = TypeInfo(self._hints['call_simple'])

        assert not info.check(5)
        assert not info.check(None)


if __name__ == '__main__':
    from unittest import main
    main()

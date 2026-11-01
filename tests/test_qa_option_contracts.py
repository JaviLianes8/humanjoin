"""Hand-written contracts for Oxford flags and overflow tail classification."""

from __future__ import annotations

from collections.abc import Callable, Iterator

import pytest

from humanjoin import format_list, join, join_max


class _ClassHook:
    def __init__(self, pretend: type[object] | None) -> None:
        self.pretend = pretend
        self.reads = 0

    def _class(self) -> type[object]:
        self.reads += 1
        if self.pretend is None:
            raise RuntimeError("private option contents")
        return self.pretend

    __class__ = property(_class)


class _Callback(_ClassHook):
    def __init__(self, pretend: type[object] | None) -> None:
        super().__init__(pretend)
        self.counts: list[int] = []

    def __call__(self, count: int) -> str:
        self.counts.append(count)
        return f"{count} more"


def _untouched() -> Iterator[str]:
    raise AssertionError("invalid options must not consume items")
    yield "unused"


@pytest.mark.parametrize("function", [join, join_max])
@pytest.mark.parametrize("pretend", [bool, None])
def test_oxford_rejects_class_hooks_before_iteration(
    function: Callable[..., str], pretend: type[object] | None
) -> None:
    value = _ClassHook(pretend)
    options: dict[str, object] = {"oxford": value}
    if function is join_max:
        options["limit"] = 1
    with pytest.raises(TypeError, match=r"^oxford must be a bool$") as caught:
        function(_untouched(), **options)
    assert caught.value.__context__ is None
    assert value.reads == 0


@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize("pretend", [str, None])
@pytest.mark.parametrize("limit", [0, 1, 2])
def test_callable_tails_never_read_class_hooks(
    function: Callable[..., str], pretend: type[object] | None, limit: int
) -> None:
    tail = _Callback(pretend)
    assert function("ab", limit=limit, more=tail) == ["2 more", "a and 1 more", "a and b"][limit]
    assert tail.counts == ([2 - limit] if limit < 2 else [])
    assert tail.reads == 0


@pytest.mark.parametrize("function", [join_max, format_list])
@pytest.mark.parametrize("pretend", [str, None])
@pytest.mark.parametrize("limit", [0, 2])
def test_invalid_tails_reject_class_hooks_before_iteration(
    function: Callable[..., str], pretend: type[object] | None, limit: int
) -> None:
    tail = _ClassHook(pretend)
    with pytest.raises(TypeError, match=r"^more must be a str or a callable$") as caught:
        function(_untouched(), limit=limit, more=tail)
    assert caught.value.__context__ is None
    assert tail.reads == 0

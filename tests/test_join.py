import pytest

from humanjoin import join, join_max


def test_zero_items_gives_an_empty_string() -> None:
    assert join([]) == ""


def test_one_item_is_returned_alone() -> None:
    assert join(["apple"]) == "apple"


def test_two_items_take_no_comma() -> None:
    assert join(["apple", "pear"]) == "apple and pear"


def test_three_items_use_the_oxford_comma_by_default() -> None:
    assert join(["apple", "pear", "plum"]) == "apple, pear, and plum"


def test_three_items_without_the_oxford_comma() -> None:
    assert join(["apple", "pear", "plum"], oxford=False) == "apple, pear and plum"


def test_custom_conjunction_or() -> None:
    assert join(["apple", "pear", "plum"], conj="or") == "apple, pear, or plum"


def test_two_items_honour_the_custom_conjunction() -> None:
    assert join(["apple", "pear"], conj="or") == "apple or pear"


def test_items_are_coerced_to_strings() -> None:
    assert join([1, 2, 3]) == "1, 2, and 3"


def test_join_max_truncates_with_a_more_tail() -> None:
    assert join_max(["a", "b", "c", "d", "e"], 2) == "a, b, and 3 more"


def test_join_max_with_a_single_remaining_item() -> None:
    assert join_max(["a", "b", "c"], 2) == "a, b, and 1 more"


def test_join_max_pluralises_through_the_template() -> None:
    assert join_max(["a", "b", "c"], 1, more="{n} others") == "a and 2 others"


def test_join_max_does_not_truncate_when_the_limit_is_high_enough() -> None:
    assert join_max(["a", "b", "c"], 5) == "a, b, and c"


def test_join_max_on_an_empty_list() -> None:
    assert join_max([], 3) == ""


def test_join_max_honours_the_conjunction_and_oxford_options() -> None:
    items = ["a", "b", "c", "d", "e"]
    assert join_max(items, 2, conj="or") == "a, b, or 3 more"
    assert join_max(items, 2, oxford=False) == "a, b and 3 more"
    assert join_max(items, 9, conj="or", oxford=False) == "a, b, c, d or e"


def test_join_max_takes_a_callable_tail_for_plurals() -> None:
    def tail(n: int) -> str:
        return f"{n} other" + ("s" if n != 1 else "")

    assert join_max(["a", "b", "c"], 2, more=tail) == "a, b, and 1 other"
    assert join_max(["a", "b", "c", "d"], 2, more=tail) == "a, b, and 2 others"


def test_join_max_with_a_zero_limit_shows_only_the_tail() -> None:
    assert join_max(["a", "b"], 0) == "2 more"


def test_join_max_with_the_limit_equal_to_the_length_hides_nothing() -> None:
    assert join_max(["a", "b", "c"], 3) == "a, b, and c"


def test_join_max_rejects_a_negative_limit() -> None:
    with pytest.raises(ValueError, match="negative"):
        join_max(["a", "b"], -1)


@pytest.mark.parametrize("limit", [True, 1.0, "1", None])
def test_join_max_rejects_a_limit_that_is_not_an_int(limit: object) -> None:
    with pytest.raises(TypeError, match="limit"):
        join_max(["a", "b"], limit)  # type: ignore[arg-type]


def test_join_max_rejects_a_tail_that_is_neither_text_nor_callable() -> None:
    with pytest.raises(TypeError, match="more"):
        join_max(["a", "b", "c"], 1, more=3)  # type: ignore[arg-type]


def test_join_max_consumes_an_iterator_once() -> None:
    assert join_max(iter(["a", "b", "c"]), 1) == "a and 2 more"


def test_join_rejects_a_conjunction_that_is_not_text() -> None:
    with pytest.raises(TypeError, match="conj"):
        join(["a", "b"], conj=None)  # type: ignore[arg-type]


def test_join_keeps_braces_in_items() -> None:
    assert join(["{0}", "{1}", "{n}"]) == "{0}, {1}, and {n}"

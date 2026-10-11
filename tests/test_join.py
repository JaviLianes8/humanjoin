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

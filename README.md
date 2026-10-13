# humanjoin

Join a list of strings into a natural-language phrase, with Oxford comma and overflow limit.

## Install

```
pip install humanjoin
```

## Usage

```python
from humanjoin import join, join_max

join([])  # ""
join(["apple"])  # "apple"
join(["apple", "pear"])  # "apple and pear"
join(["apple", "pear", "plum"])  # "apple, pear, and plum"
join(["apple", "pear", "plum"], oxford=False)  # "apple, pear and plum"
join(["red", "green", "blue"], conj="or")  # "red, green, or blue"
join([1, 2, 3])  # "1, 2, and 3"

join_max(["a", "b", "c", "d", "e"], 2)  # "a, b, and 3 more"
join_max(["a", "b", "c"], 2)  # "a, b, and 1 more"
join_max(["a", "b", "c"], 1, more="{n} others")  # "a and 2 others"
```

`join` covers the empty, single, pair and many cases: a single item is returned alone, a
pair is joined by the conjunction with no comma, and three or more use commas with the
Oxford comma on by default. `join_max` keeps at most `limit` items and folds the rest into
a tail rendered from the `more` template, which receives the remaining count as `n`.

## Why

Joining a list into readable prose is written again in every project, and the small details
(no comma for two items, the Oxford comma toggle, an "and N more" overflow) are easy to get
wrong. `humanize.natural_list` offers no Oxford comma and no overflow limit. `inflect.join`
has the Oxford comma but pulls in extra dependencies, and the overflow limit exists in
neither. This is a typed, zero-dependency primitive for exactly those cases.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/

## Summary

Combining `Q` objects with the `|` operator raises `TypeError: cannot pickle 'dict_keys' object` when one of the `Q` objects references a non-pickleable object, such as a `dict_keys` view. Creating the `Q` object on its own works. Only the `|` combination fails.

## Steps to reproduce

1. Import `Q`: `from django.db.models import Q`
2. Create a `Q` object whose lookup value is a `dict_keys` object: `Q(x__in={}.keys())`. This succeeds.
3. Combine an empty `Q` with that object using `|`: `Q() | Q(x__in={}.keys())`

## Observed behavior

- Step 2 succeeds and returns `<Q: (AND: ('x__in', dict_keys([])))>`.
- Step 3 raises `TypeError: cannot pickle 'dict_keys' object`.

A workaround for this particular example is `Q() | Q(x__in={})`. The reporter says passing `.keys()` should still work.

## Expected behavior

Applying `|` to a `Q` object that references a non-pickleable object such as `dict_keys` should not crash. It should return the combined `Q` object, just as constructing `Q(x__in={}.keys())` does on its own.

## Stack trace / error output

The original report abbreviates the traceback:

```
>>> Q() | Q(x__in={}.keys())
Traceback (most recent call last):
...
TypeError: cannot pickle 'dict_keys' object
```

The full stack trace is not provided in the original report.

## Test case

This minimal check is derived from the reproduction snippet. The final line should run without raising `TypeError`:

```python
from django.db.models import Q

Q(x__in={}.keys())            # works
Q() | Q(x__in={}.keys())      # currently raises TypeError: cannot pickle 'dict_keys' object
```

## Code example

```python
>>> from django.db.models import Q
>>> Q(x__in={}.keys())
<Q: (AND: ('x__in', dict_keys([])))>
>>> Q() | Q(x__in={}.keys())
Traceback (most recent call last):
...
TypeError: cannot pickle 'dict_keys' object
```

## Version and environment

Not provided in the original report.
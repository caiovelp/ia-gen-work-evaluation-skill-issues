## Summary

`uniq` gives silently wrong results when the list passed to it is modified while iterating over its output. Python raises an error when a dictionary or set changes size during iteration. `uniq` raises no error and simply yields an incomplete sequence.

## Steps to reproduce

1. Create a list: `f = list('THISTLE')`.
2. Iterate over `uniq(f)`. Inside the loop, remove each yielded element from `f` and output it:
   ```python
   for i in uniq(f):
       f.remove(i)
       i
   ```
3. Look at the values yielded.

## Observed behavior

The loop runs without error but yields only some of the unique elements:

```
'T'
'I'
'L'
```

The unique elements of `'THISTLE'` are `T`, `H`, `I`, `S`, `L` and `E`, so this output is wrong. Nothing warns the user.

## Expected behavior

`uniq` should detect that the list passed to it has changed size during iteration. It should then raise a `RuntimeError`, like the one Python raises for dictionaries and sets. For comparison, here is what Python does with a dictionary (the `multiset` result) that is modified during iteration:

```python
>>> multiset('THISTLE')
{'T': 2, 'H': 1, 'I': 1, 'S': 1, 'L': 1, 'E': 1}
>>> for i in _:
...   _.pop(i)
...
2
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: dictionary changed size during iteration
```

## Stack trace / error output

No error is produced for `uniq`, which is the problem. The only traceback in the report is the reference behavior for a dictionary, shown above:

```
RuntimeError: dictionary changed size during iteration
```

## Test case

Minimal test derived from the report. The report does not give the module `uniq` is imported from.

```python
import pytest

def test_uniq_raises_when_argument_modified():
    f = list('THISTLE')
    with pytest.raises(RuntimeError):
        for i in uniq(f):
            f.remove(i)
```

## Code example

From the original report:

```python
>>> f=list('THISTLE')
>>> for i in uniq(f):
...   f.remove(i)
...   i
...
'T'
'I'
'L'
```

## Version and environment

Not provided in the original report.
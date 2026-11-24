## Summary

`LabelEncoder.transform([])` behaves differently depending on the data type used to fit the encoder. After fitting on integer labels, transforming an empty list returns an empty array. After fitting on string labels, the same call raises a `TypeError` from `np.searchsorted` because a `float64` array cannot be cast to `<U32`.

## Steps to reproduce

1. Import `LabelEncoder` from `sklearn.preprocessing` and create an instance: `le = LabelEncoder()`.
2. Fit it on integer labels: `le.fit([1, 2])`.
3. Call `le.transform([])`. This returns `array([], dtype=int64)` as expected.
4. Fit the same encoder on string labels: `le.fit(["a", "b"])`.
5. Call `le.transform([])` again. This raises a `TypeError`.

## Observed behavior

- Fitted on `[1, 2]`: `le.transform([])` returns `array([], dtype=int64)`.
- Fitted on `["a", "b"]`: `le.transform([])` raises `TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'`.

## Expected behavior

`le.transform([])` should return an empty array in both cases, whatever data type was used to fit the encoder.

## Stack trace / error output

```
Traceback (most recent call last):
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 57, in _wrapfunc
    return getattr(obj, method)(*args, **kwds)
TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "[...]\Python36\lib\site-packages\sklearn\preprocessing\label.py", line 134, in transform
    return np.searchsorted(self.classes_, y)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 1075, in searchsorted
    return _wrapfunc(a, 'searchsorted', v, side=side, sorter=sorter)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 67, in _wrapfunc
    return _wrapit(obj, method, *args, **kwds)
  File "[...]\Python36\lib\site-packages\numpy\core\fromnumeric.py", line 47, in _wrapit
    result = getattr(asarray(obj), method)(*args, **kwds)
TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'
```

## Test case

Minimal test derived from the reproduction in the report:

```python
from sklearn.preprocessing import LabelEncoder


def test_label_encoder_transform_empty_list_numeric_fit():
    le = LabelEncoder()
    le.fit([1, 2])
    result = le.transform([])
    assert len(result) == 0  # passes in the reported version


def test_label_encoder_transform_empty_list_string_fit():
    le = LabelEncoder()
    le.fit(["a", "b"])
    result = le.transform([])  # raises TypeError in the reported version
    assert len(result) == 0
```

## Code example

Interactive session from the original report:

```python
>>> from sklearn.preprocessing import LabelEncoder
>>> le = LabelEncoder()
>>> le.fit([1,2])
LabelEncoder()
>>> le.transform([])
array([], dtype=int64)
>>> le.fit(["a","b"])
LabelEncoder()
>>> le.transform([])
# TypeError: Cannot cast array data from dtype('float64') to dtype('<U32') according to the rule 'safe'
```

## Version and environment

- Python 3.6.3
- scikit-learn 0.19.1
- NumPy version: Not provided in the original report.
- Operating system: Not provided in the original report. The `[...]\Python36\lib\site-packages` paths in the traceback suggest Windows.
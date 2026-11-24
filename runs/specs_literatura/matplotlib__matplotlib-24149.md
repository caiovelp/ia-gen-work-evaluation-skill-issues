## Summary

On Matplotlib 3.6.1, `ax.bar` raises `StopIteration` when the x positions are all NaN. On 3.6.0 the same call returned a `BarCollection`. The failure depends on the x position: NaN x raises, while NaN height with a finite x works.

This breaks seaborn's histogram function. Seaborn draws and then removes a "phantom" bar to advance the color cycle.

The reporter suspects a link to this 3.6.1 release-note entry: "Fix barplot being empty when first element is NaN".

## Steps to reproduce

1. Install Matplotlib 3.6.1 (installed via pip on macOS in the original report).
2. Run:
   ```python
   import numpy as np
   import matplotlib.pyplot as plt
   f, ax = plt.subplots()
   ax.bar([np.nan], [np.nan])
   ```
3. A `StopIteration` exception is raised.

Further variants from the report:

| Call | Result on 3.6.1 |
|---|---|
| `ax.bar([np.nan], [np.nan])` | Raises |
| `ax.bar([np.nan], [0])` | Raises |
| `ax.bar([0], [np.nan])` | Works |

## Observed behavior

`ax.bar` raises `StopIteration` whenever all x values are NaN, whatever the height. The exception comes from `cbook._safe_first_finite`, called from `Axes._convert_dx` while converting `width`. No finite value is found in `x0`, so `next(...)` on the generator raises `StopIteration`. This exception is not among those caught there (`TypeError`, `IndexError`, `KeyError`).

## Expected behavior

As on Matplotlib 3.6.0, `ax.bar([np.nan], [np.nan])` should return a `BarCollection` containing one `Rectangle` whose `x` and `height` are `nan`. No exception should be raised.

## Stack trace / error output

Note: the traceback was produced by `ax.bar([np.nan], [np.nan])[0].get_x()`, a slight variant of the reproduction snippet.

```python-traceback
---------------------------------------------------------------------------
StopIteration                             Traceback (most recent call last)
Cell In [1], line 4
      2 import matplotlib.pyplot as plt
      3 f, ax = plt.subplots()
----> 4 ax.bar([np.nan], [np.nan])[0].get_x()

File ~/miniconda/envs/py310/lib/python3.10/site-packages/matplotlib/__init__.py:1423, in _preprocess_data.<locals>.inner(ax, data, *args, **kwargs)
   1420 @functools.wraps(func)
   1421 def inner(ax, *args, data=None, **kwargs):
   1422     if data is None:
-> 1423         return func(ax, *map(sanitize_sequence, args), **kwargs)
   1425     bound = new_sig.bind(ax, *args, **kwargs)
   1426     auto_label = (bound.arguments.get(label_namer)
   1427                   or bound.kwargs.get(label_namer))

File ~/miniconda/envs/py310/lib/python3.10/site-packages/matplotlib/axes/_axes.py:2373, in Axes.bar(self, x, height, width, bottom, align, **kwargs)
   2371 x0 = x
   2372 x = np.asarray(self.convert_xunits(x))
-> 2373 width = self._convert_dx(width, x0, x, self.convert_xunits)
   2374 if xerr is not None:
   2375     xerr = self._convert_dx(xerr, x0, x, self.convert_xunits)

File ~/miniconda/envs/py310/lib/python3.10/site-packages/matplotlib/axes/_axes.py:2182, in Axes._convert_dx(dx, x0, xconv, convert)
   2170 try:
   2171     # attempt to add the width to x0; this works for
   2172     # datetime+timedelta, for instance
   (...)
   2179     # removes the units from unit packages like `pint` that
   2180     # wrap numpy arrays.
   2181     try:
-> 2182         x0 = cbook._safe_first_finite(x0)
   2183     except (TypeError, IndexError, KeyError):
   2184         pass

File ~/miniconda/envs/py310/lib/python3.10/site-packages/matplotlib/cbook/__init__.py:1749, in _safe_first_finite(obj, skip_nonfinite)
   1746     raise RuntimeError("matplotlib does not "
   1747                        "support generators as input")
   1748 else:
-> 1749     return next(val for val in obj if safe_isfinite(val))

StopIteration: 
```

## Test case

Minimal test derived from the reproduction and the expected 3.6.0 behavior:

```python
import numpy as np
import matplotlib.pyplot as plt


def test_bar_all_nan():
    f, ax = plt.subplots()
    bars = ax.bar([np.nan], [np.nan])  # raises StopIteration on 3.6.1
    assert len(bars) == 1
    assert np.isnan(bars[0].get_x())
    assert np.isnan(bars[0].get_height())


def test_bar_nan_x_finite_height():
    f, ax = plt.subplots()
    ax.bar([np.nan], [0])  # raises StopIteration on 3.6.1


def test_bar_finite_x_nan_height():
    f, ax = plt.subplots()
    ax.bar([0], [np.nan])  # works on 3.6.1
```

## Code example

```python
import numpy as np
import matplotlib.pyplot as plt
f, ax = plt.subplots()
ax.bar([np.nan], [np.nan])

ax.bar([np.nan], [0])  # Raises
ax.bar([0], [np.nan])  # Works
```

## Version and environment

- Matplotlib version: 3.6.1 (regression; 3.6.0 behaves as expected)
- Operating system: macOS
- Installation: pip
- Python version: not stated. The traceback paths suggest a Python 3.10 conda environment (`~/miniconda/envs/py310/lib/python3.10/...`).
- Matplotlib backend: Not provided in the original report.
- Jupyter version: Not provided in the original report.
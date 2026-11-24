## Summary

Matplotlib 3.6.0 emits a `UserWarning` about an incompatible layout engine when `plt.subplots_adjust` is called on a figure created with `constrained_layout=False`. The reporter says the same happens with `bbox_inches='tight'`, and that earlier versions did not warn. The plot itself renders correctly. The warning disappears when the `constrained_layout=False` argument is removed.

## Steps to reproduce

1. Create a figure with two subplots and explicitly pass `constrained_layout=False`:
   `fig, ax = plt.subplots(1, 2, figsize=(8, 2), constrained_layout=False)`
2. Plot data on both axes.
3. Call `plt.subplots_adjust(wspace=0)`.
4. Observe that a `UserWarning` is emitted.

## Observed behavior

The plot is produced correctly, but a `UserWarning` says the figure uses a layout engine that is incompatible with `subplots_adjust` and/or `tight_layout`, and that `subplots_adjust` was not called. This happens even though `constrained_layout=False` was passed.

The reporter says the same warning appears with other layout settings such as `bbox_inches='tight'`. Removing `constrained_layout=False` from the `plt.subplots` call makes the warning go away.

## Expected behavior

No warning should be emitted when `constrained_layout=False` is passed. According to the reporter, previous versions did not emit this warning.

## Stack trace / error output

```
/var/folders/ss/pfgdfm2x7_s4cyw2v0b_t7q80000gn/T/ipykernel_76923/4170965423.py:7: UserWarning: This figure was using a layout engine that is incompatible with subplots_adjust and/or tight_layout; not calling subplots_adjust.
  plt.subplots_adjust(wspace=0)
```

## Test case

A minimal test derived from the reproduction code in the report:

```python
import warnings
import matplotlib.pyplot as plt
import numpy as np

def test_subplots_adjust_no_warning_with_constrained_layout_false():
    a = np.linspace(0, 2 * np.pi, 100)
    fig, ax = plt.subplots(1, 2, figsize=(8, 2), constrained_layout=False)
    ax[0].plot(a, np.sin(a))
    ax[1].plot(a, np.cos(a))
    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        plt.subplots_adjust(wspace=0)
    assert not [w for w in record if issubclass(w.category, UserWarning)]
```

## Code example

```python
import matplotlib.pyplot as plt
import numpy as np
a = np.linspace(0,2*np.pi,100)
b = np.sin(a)
c = np.cos(a)
fig,ax = plt.subplots(1,2,figsize=(8,2),constrained_layout=False)
ax[0].plot(a,b)
ax[1].plot(a,c)
plt.subplots_adjust(wspace=0)
```

## Version and environment

- Matplotlib version: 3.6.0
- Operating system: OS/X
- Installation: conda
- Matplotlib backend: Not provided in the original report.
- Python version: Not provided in the original report.
- Jupyter version: Not provided in the original report. The warning path (`ipykernel_76923`) suggests the code was run in an IPython/Jupyter kernel.
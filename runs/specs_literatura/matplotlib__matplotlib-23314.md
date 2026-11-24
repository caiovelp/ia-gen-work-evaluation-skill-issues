## Summary

For subplots created with `projection="3d"`, calling `Axes.set_visible(False)` has no effect. The 3D subplot is still drawn.

## Steps to reproduce

1. Create a figure with two subplots using the 3D projection: `plt.subplots(1, 2, subplot_kw={'projection': '3d'})`.
2. Plot a point on each axes: `ax1.scatter(1, 1, 1)` and `ax2.scatter(1, 1, 1, c='r')`.
3. Hide the first axes with `ax1.set_visible(False)`.
4. Show the figure with `plt.show()`.
5. Look at the left subplot (`ax1`).

## Observed behavior

The subplot `ax1` is still visible, even though `set_visible(False)` was called on it.

## Expected behavior

The subplot `ax1` is not shown after `set_visible(False)` is called on it.

## Stack trace / error output

Not provided in the original report.

## Test case

This minimal reproduction comes from the report's snippet. The unused `GridSpec` import has been removed. Run it and check the figure by eye:

```python
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})
ax1.scatter(1, 1, 1)
ax2.scatter(1, 1, 1, c='r')
ax1.set_visible(False)

plt.show()
# Expected: only the right subplot (ax2, red point) is shown.
# Observed: the left subplot (ax1) is still shown.
```

## Code example

The original reproduction code from the report:

```python
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

fig, (ax1, ax2) = plt.subplots(1, 2, subplot_kw={'projection': '3d'})
ax1.scatter(1,1,1)
ax2.scatter(1,1,1, c='r')
ax1.set_visible(False)

plt.show()
```

## Version and environment

- Matplotlib version: 3.4.2
- Matplotlib backend: Qt5Agg
- Python version: 3.8.10
- Operating system: Not provided in the original report.
- Jupyter version: Not provided in the original report.
- Installation method: Not provided in the original report.
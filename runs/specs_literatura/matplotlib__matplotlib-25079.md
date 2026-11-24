## Summary

In Matplotlib 3.6.3, replacing the norm of a mappable with a `LogNorm` after a colorbar has been attached raises `ValueError: Invalid vmin or vmax` on the next draw. This pattern is common in interactive code. The same code worked in Matplotlib 3.6.2, so this is a regression.

The reporter notes that `vmin` and `vmax` are explicitly set to values valid for `LogNorm` (1 and 5). The input data has no negative or zero values (it is drawn uniformly from [1, 5)).

## Steps to reproduce

1. Use Matplotlib 3.6.3. The reporter reproduced this with Qt5Agg, TkAgg and agg.
2. Create a 25×25 array of random values uniformly drawn from [1, 5) with `np.random.default_rng(0)`.
3. Create a figure with `layout="constrained"` and plot the array with `ax.pcolormesh(img)`.
4. Add a colorbar for the mesh with `fig.colorbar(plot, ax=ax)`.
5. Turn on interactive mode (`plt.ion()`), show the figure (`fig.show()`) and call `plt.pause(0.5)`.
6. Set `plot.norm = LogNorm(1, 5)`.
7. Call `plot.autoscale()`.
8. Call `plt.pause(0.5)` to trigger a redraw.
9. The redraw fails with `ValueError: Invalid vmin or vmax`.

## Observed behavior

When the figure is redrawn after the norm change, `LogNorm.__call__` raises `ValueError: Invalid vmin or vmax`. The error comes from `update_scalarmappable` → `to_rgba` → `self.norm(x)` while the `QuadMesh` is being drawn. The mappable and colorbar are not updated with the new norm.

## Expected behavior

Setting the new norm should work, as it did in Matplotlib 3.6.2. Both the colorbar and the mappable should update to use the new `LogNorm`.

## Stack trace / error output

```
Traceback (most recent call last):
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/backends/backend_qt.py", line 454, in _draw_idle
    self.draw()
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/backends/backend_agg.py", line 405, in draw
    self.figure.draw(self.renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/artist.py", line 74, in draw_wrapper
    result = draw(artist, renderer, *args, **kwargs)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/figure.py", line 3082, in draw
    mimage._draw_list_compositing_images(
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/axes/_base.py", line 3100, in draw
    mimage._draw_list_compositing_images(
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/image.py", line 131, in _draw_list_compositing_images
    a.draw(renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/artist.py", line 51, in draw_wrapper
    return draw(artist, renderer)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/collections.py", line 2148, in draw
    self.update_scalarmappable()
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/collections.py", line 891, in update_scalarmappable
    self._mapped_colors = self.to_rgba(self._A, self._alpha)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/cm.py", line 511, in to_rgba
    x = self.norm(x)
  File "/home/mnoethe/.local/conda/envs/cta-dev/lib/python3.9/site-packages/matplotlib/colors.py", line 1694, in __call__
    raise ValueError("Invalid vmin or vmax")
ValueError: Invalid vmin or vmax
```

## Test case

This test case is derived directly from the reproduction code in the report and uses the same calls. It fails on 3.6.3 with the error above and is expected to pass, as it did on 3.6.2.

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np


def test_set_lognorm_after_colorbar_created():
    rng = np.random.default_rng(0)
    img = rng.uniform(1, 5, (25, 25))

    fig, ax = plt.subplots(layout="constrained")
    plot = ax.pcolormesh(img)
    cbar = fig.colorbar(plot, ax=ax)

    vmin = 1
    vmax = 5

    plt.ion()
    fig.show()
    plt.pause(0.5)

    plot.norm = LogNorm(vmin, vmax)
    plot.autoscale()
    plt.pause(0.5)  # 3.6.3: ValueError: Invalid vmin or vmax
```

## Code example

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

# create some random data to fill a 2d plot
rng = np.random.default_rng(0)
img = rng.uniform(1, 5, (25, 25))

# plot it
fig, ax = plt.subplots(layout="constrained")
plot = ax.pcolormesh(img)
cbar = fig.colorbar(plot, ax=ax)

vmin = 1
vmax = 5

plt.ion()
fig.show()
plt.pause(0.5)

plot.norm = LogNorm(vmin, vmax)
plot.autoscale()
plt.pause(0.5)
```

## Version and environment

- **Matplotlib version:** 3.6.3 (fails); 3.6.2 (works)
- **Backend:** Multiple backends tested, same error in all (Qt5Agg, TkAgg, agg, ...)
- **Python version:** 3.9.15
- **Operating system:** Linux
- **Jupyter:** Not used
- **Installation:** conda
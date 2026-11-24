## Summary

Creating an `mpl_toolkits.axes_grid1.AxesGrid` with cartopy's `GeoAxes` as `axes_class` raises `TypeError: 'method' object is not subscriptable`.

The reporter attributes this to a difference in the `axis` attribute:

- On `mpl_toolkits.axes_grid1.mpl_axes.Axes`, `axis` can be indexed with keys such as `ax.axis["bottom"]`.
- On other axes classes, such as `GeoAxes`, `axis` is only a callable method.

The error is raised in `mpl_toolkits.axes_grid1.axes_grid._tick_only`, which indexes `ax.axis` by key. `AxesGrid.__init__` reaches it through `set_label_mode`.

## Steps to reproduce

1. Install Matplotlib 3.1.2 and cartopy 0.17.0.
2. Create a figure with `plt.figure()`.
3. Define `axes_class = (GeoAxes, dict(map_projection=PlateCarree()))`.
4. Create `AxesGrid(fig, 111, nrows_ncols=(1, 1), axes_class=axes_class)`.
5. Observe the `TypeError` raised during grid construction.

## Observed behavior

`AxesGrid` construction fails with `TypeError: 'method' object is not subscriptable`. The failing call chain is:

1. `AxesGrid.__init__`
2. `set_label_mode(label_mode)`
3. `_tick_only(ax, bottom_on=False, left_on=False)`
4. `ax.axis["bottom"].toggle(...)`

`ax.axis` is a method on `GeoAxes`, so it cannot be indexed.

## Expected behavior

The original report left the "Expected outcome" section empty. The title ("Error creating AxisGrid with non-default axis class") implies the expectation that `AxesGrid` can be created with a non-default axes class such as `GeoAxes` without raising an error.

## Stack trace / error output

```
Traceback (most recent call last):

  File "/home/jonasg/stuff/bugreport_mpl_toolkits_AxesGrid.py", line 16, in <module>
    axes_class=axes_class)

  File "/home/jonasg/miniconda3/envs/pya/lib/python3.7/site-packages/mpl_toolkits/axes_grid1/axes_grid.py", line 618, in __init__
    self.set_label_mode(label_mode)

  File "/home/jonasg/miniconda3/envs/pya/lib/python3.7/site-packages/mpl_toolkits/axes_grid1/axes_grid.py", line 389, in set_label_mode
    _tick_only(ax, bottom_on=False, left_on=False)

  File "/home/jonasg/miniconda3/envs/pya/lib/python3.7/site-packages/mpl_toolkits/axes_grid1/axes_grid.py", line 27, in _tick_only
    ax.axis["bottom"].toggle(ticklabels=bottom_off, label=bottom_off)

TypeError: 'method' object is not subscriptable
```

## Test case

This minimal test is derived from the reproduction snippet. It passes if `AxesGrid` is constructed without raising:

```python
import matplotlib.pyplot as plt
from cartopy.crs import PlateCarree
from cartopy.mpl.geoaxes import GeoAxes
from mpl_toolkits.axes_grid1 import AxesGrid


def test_axesgrid_with_geoaxes_axes_class():
    fig = plt.figure()
    axes_class = (GeoAxes, dict(map_projection=PlateCarree()))
    AxesGrid(fig, 111, nrows_ncols=(1, 1), axes_class=axes_class)
```

## Code example

```python
import matplotlib.pyplot as plt
from cartopy.crs import PlateCarree
from cartopy.mpl.geoaxes import GeoAxes
from mpl_toolkits.axes_grid1 import AxesGrid

fig = plt.figure()
axes_class = (GeoAxes, dict(map_projection=PlateCarree()))
gr = AxesGrid(fig, 111, nrows_ncols=(1,1),
              axes_class=axes_class)
```

## Version and environment

- Operating system: Ubuntu 18.04.4 LTS
- Matplotlib version: 3.1.2 (conda-forge; `matplotlib` 3.1.2 py37_1, `matplotlib-base` 3.1.2 py37h250f245_1)
- Matplotlib backend: Qt5Agg
- Python version: 3.7.6 (conda-forge)
- cartopy: 0.17.0 (conda-forge, build py37hd759880_1006)
- Other relevant packages from the reporter's conda environment:
  - numpy 1.17.5
  - pyproj 1.9.6
  - proj4 5.2.0
  - shapely 1.6.4
  - pyqt 5.12.3
  - qt 5.12.5
- Installation: conda environment (miniconda3). The original report includes the full `conda list` output.
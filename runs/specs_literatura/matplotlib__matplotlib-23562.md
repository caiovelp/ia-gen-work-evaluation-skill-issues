## Summary

Calling `get_facecolors()` on the `Poly3DCollection` returned by `Axes3D.plot_surface()` raises `AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'`.

## Steps to reproduce

1. Create a grid and surface data with NumPy:
   ```python
   y, x = np.ogrid[1:10:100j, 1:10:100j]
   z2 = np.cos(x)**3 - np.sin(y)**2
   ```
2. Create a figure and add a 3D subplot with `fig.add_subplot(111, projection='3d')`.
3. Plot the surface with a colormap: `r = ax.plot_surface(x, y, z2, cmap='hot')`.
4. Call `r.get_facecolors()` on the returned object.

## Observed behavior

The call to `r.get_facecolors()` fails with `AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'`.

## Expected behavior

The report does not state this explicitly. Its title and wording imply that `get_facecolors()` should return the surface's face colors without raising an `AttributeError`.

## Stack trace / error output

```
AttributeError                            Traceback (most recent call last)
<ipython-input-13-de0f41d662cd> in <module>()
----> 1 r.get_facecolors()

/home/oliver/.virtualenvs/mpl/local/lib/python2.7/site-packages/mpl_toolkits/mplot3d/art3d.pyc in get_facecolors(self)
    634
    635     def get_facecolors(self):
--> 636         return self._facecolors2d
    637     get_facecolor = get_facecolors
    638

AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'
```

## Test case

Minimal test case derived from the reproduction snippet in the report:

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 (registers the '3d' projection)


def test_plot_surface_get_facecolors():
    y, x = np.ogrid[1:10:100j, 1:10:100j]
    z2 = np.cos(x)**3 - np.sin(y)**2
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    r = ax.plot_surface(x, y, z2, cmap='hot')
    # Currently raises AttributeError: 'Poly3DCollection' object has no attribute '_facecolors2d'
    r.get_facecolors()
```

## Code example

Original reproduction script from the report:

```python
import numpy as np
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

y,x = np.ogrid[1:10:100j, 1:10:100j]
z2 = np.cos(x)**3 - np.sin(y)**2
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
r = ax.plot_surface(x,y,z2, cmap='hot')
r.get_facecolors()
```

The failing line in `mpl_toolkits/mplot3d/art3d.py`, as shown in the traceback:

```python
def get_facecolors(self):
    return self._facecolors2d
get_facecolor = get_facecolors
```

## Version and environment

- Matplotlib: tested with 1.3.1 and 1.4.2 (fails on both).
- Python: 2.7, according to the virtualenv path in the traceback (`.../lib/python2.7/site-packages/...`).
- The traceback came from an IPython session (`<ipython-input-13-...>`).
- OS: Not provided in the original report.
- The issue was forwarded from the matplotlib users mailing list (thread with the same title).
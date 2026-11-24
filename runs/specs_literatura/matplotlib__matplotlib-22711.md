## Summary

Passing an initial value (`valinit`) to the `matplotlib.widgets.RangeSlider` constructor raises an `IndexError`, so the slider cannot be created with user-defined initial values. The error is raised in `RangeSlider.set_val` (`matplotlib/widgets.py`, line 915), which `__init__` calls with `valinit` (line 778). The failing statement is `xy[4] = val[0], .25`. It writes to index 4 of the slider polygon's vertex array, but that array has only 4 rows.

## Steps to reproduce

1. Install Matplotlib 3.5.1 (via pip) on Python 3.8 (macOS).
2. Create a figure and add an axes for the slider, e.g. `slider_ax = fig.add_axes([0.20, 0.1, 0.60, 0.03])`.
3. Create a horizontal `RangeSlider` with an explicit initial value:
   `RangeSlider(slider_ax, "Threshold", img.min(), img.max(), valinit=[0.0, 0.0])`
   Here `img` is a 128×128 array from `np.random.randn` with seed `19680801`.
4. Observe that the constructor raises an `IndexError` before the slider is shown.

## Observed behavior

Constructing the `RangeSlider` with `valinit=[0.0, 0.0]` fails. `RangeSlider.__init__` calls `self.set_val(valinit)`, and in the horizontal-orientation branch the statement `xy[4] = val[0], .25` raises:

```
IndexError: index 4 is out of bounds for axis 0 with size 4
```

## Expected behavior

The `RangeSlider` is created and displayed with the user-supplied initial values (`valinit`).

## Stack trace / error output

```
  File "<ipython-input-52-b704c53e18d4>", line 19, in <module>
    slider = RangeSlider(slider_ax, "Threshold", img.min(), img.max(),valinit=[0.0,0.0])

  File "/Users/Vincent/opt/anaconda3/envs/py38/lib/python3.8/site-packages/matplotlib/widgets.py", line 778, in __init__
    self.set_val(valinit)

  File "/Users/Vincent/opt/anaconda3/envs/py38/lib/python3.8/site-packages/matplotlib/widgets.py", line 915, in set_val
    xy[4] = val[0], .25

IndexError: index 4 is out of bounds for axis 0 with size 4
```

## Test case

Minimal reproduction derived from the original report's script:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider

np.random.seed(19680801)
img = np.random.randn(128, 128)

fig = plt.figure()
slider_ax = fig.add_axes([0.20, 0.1, 0.60, 0.03])

# Raises: IndexError: index 4 is out of bounds for axis 0 with size 4
slider = RangeSlider(slider_ax, "Threshold", img.min(), img.max(), valinit=[0.0, 0.0])
```

## Code example

Full script from the original report:

```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RangeSlider

# generate a fake image
np.random.seed(19680801)
N = 128
img = np.random.randn(N, N)

fig, axs = plt.subplots(1, 2, figsize=(10, 5))
fig.subplots_adjust(bottom=0.25)

im = axs[0].imshow(img)
axs[1].hist(img.flatten(), bins='auto')
axs[1].set_title('Histogram of pixel intensities')

# Create the RangeSlider
slider_ax = fig.add_axes([0.20, 0.1, 0.60, 0.03])
slider = RangeSlider(slider_ax, "Threshold", img.min(), img.max(),valinit=[0.0,0.0])

# Create the Vertical lines on the histogram
lower_limit_line = axs[1].axvline(slider.val[0], color='k')
upper_limit_line = axs[1].axvline(slider.val[1], color='k')


def update(val):
    # The val passed to a callback by the RangeSlider will
    # be a tuple of (min, max)

    # Update the image's colormap
    im.norm.vmin = val[0]
    im.norm.vmax = val[1]

    # Update the position of the vertical lines
    lower_limit_line.set_xdata([val[0], val[0]])
    upper_limit_line.set_xdata([val[1], val[1]])

    # Redraw the figure to ensure it updates
    fig.canvas.draw_idle()


slider.on_changed(update)
plt.show()
```

## Version and environment

- Matplotlib version: 3.5.1
- Python version: 3.8
- Operating system: macOS (OSX)
- Installation: pip (the traceback path points to an Anaconda environment, `anaconda3/envs/py38`)
- Run from: an IPython/Jupyter-style session (per the `<ipython-input-…>` frame); the Jupyter version was not provided in the original report.
- Matplotlib backend: Not provided in the original report.
## Summary

After replacing the `norm` of a mappable (e.g. an `imshow` image) with a new `LogNorm` instance, the attached colorbar cannot be updated to match. `Colorbar.update_normal(mappable)` has no effect, and `Colorbar.update_bruteforce(mappable)` raises a `ZeroDivisionError`.

## Steps to reproduce

1. Create an image with positive, log-normally distributed values: `img = 10**np.random.normal(1, 1, size=(50, 50))`.
2. Plot it with `ax.imshow(img, cmap='gray')`. This uses the default linear norm.
3. Add a colorbar with `fig.colorbar(plot, ax=ax)`.
4. Replace the image's norm: `plot.norm = LogNorm()`.
5. Call `cb.update_normal(plot)`. The colorbar does not change.
6. Call `cb.update_bruteforce(plot)`. A `ZeroDivisionError` is raised.

## Observed behavior

- `cb.update_normal(plot)` has no visible effect. The colorbar does not reflect the new `LogNorm`.
- `cb.update_bruteforce(plot)` raises `ZeroDivisionError: division by zero` in `LogNorm.inverse` (`colors.py`, line 1011). It is called from `Colorbar._process_values`.

## Expected behavior

After the mappable's norm is changed to `LogNorm`, calling the colorbar update method should redraw the colorbar using the new norm, without raising an error.

## Stack trace / error output

```
Traceback (most recent call last):
  File "test_norm.py", line 12, in <module>
    cb.update_bruteforce(plot)
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 967, in update_bruteforce
    self.draw_all()
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 342, in draw_all
    self._process_values()
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colorbar.py", line 664, in _process_values
    b = self.norm.inverse(self._uniform_y(self.cmap.N + 1))
  File "/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/colors.py", line 1011, in inverse
    return vmin * ma.power((vmax / vmin), val)
ZeroDivisionError: division by zero
```

## Test case

Minimal reproduction taken from the report. The `update_bruteforce` call is the one expected to fail:

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

img = 10**np.random.normal(1, 1, size=(50, 50))

fig, ax = plt.subplots(1, 1)
plot = ax.imshow(img, cmap='gray')
cb = fig.colorbar(plot, ax=ax)
plot.norm = LogNorm()
cb.update_bruteforce(plot)  # raises ZeroDivisionError
```

## Code example

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np

img = 10**np.random.normal(1, 1, size=(50, 50))

fig, ax = plt.subplots(1, 1)
plot = ax.imshow(img, cmap='gray')
cb = fig.colorbar(plot, ax=ax)
plot.norm = LogNorm()
cb.update_normal(plot)  # no effect
cb.update_bruteforce(plot)  # throws ZeroDivisionError
plt.show()
```

## Version and environment

- Matplotlib version: Not provided in the original report.
- Python 3.4, Anaconda distribution. This is inferred from the traceback path `/home/maxnoe/.local/anaconda3/lib/python3.4/site-packages/matplotlib/`.
- Operating system: Not provided explicitly. The `/home/...` path suggests a Linux/Unix-like system.
- Backend: Not provided in the original report.
## Summary

In Matplotlib 3.5.0 (main), moving the mouse over an image drawn with `imshow` and a `BoundaryNorm` raises `ValueError: BoundaryNorm is not invertible` from `format_cursor_data`, and interaction with the figure stops.

## Steps to reproduce

1. Run the following script:
   ```python
   import matplotlib.pyplot as plt
   import numpy as np
   import matplotlib as mpl

   fig, ax = plt.subplots()
   norm = mpl.colors.BoundaryNorm(np.linspace(-4, 4, 5), 256)
   X = np.random.randn(10, 10)
   pc = ax.imshow(X, cmap='RdBu_r', norm=norm)
   ```
2. Show the figure in an interactive window.
3. Move the mouse cursor over the image.

## Observed behavior

When the cursor is over the image, `format_cursor_data` calls `self.norm.inverse(...)`. `BoundaryNorm.inverse` raises `ValueError: BoundaryNorm is not invertible`. Interaction with the figure then stops.

## Expected behavior

Moving the mouse over an image that uses a `BoundaryNorm` should not raise an exception, and interaction with the figure should keep working.

## Stack trace / error output

```
File "/Users/jklymak/matplotlib/lib/matplotlib/artist.py", line 1282, in format_cursor_data
    neighbors = self.norm.inverse(
  File "/Users/jklymak/matplotlib/lib/matplotlib/colors.py", line 1829, in inverse
    raise ValueError("BoundaryNorm is not invertible")
ValueError: BoundaryNorm is not invertible
```

## Test case

Not provided in the original report. The error is triggered interactively, by mousing over the image created in the code example below.

## Code example

```python
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl

fig, ax = plt.subplots()
norm = mpl.colors.BoundaryNorm(np.linspace(-4, 4, 5), 256)
X = np.random.randn(10, 10)
pc = ax.imshow(X, cmap='RdBu_r', norm=norm)
```

## Version and environment

- Matplotlib: 3.5.0 / main. The traceback paths show a source checkout at `/Users/jklymak/matplotlib`.
- Operating system, Python version, and backend: Not provided in the original report.
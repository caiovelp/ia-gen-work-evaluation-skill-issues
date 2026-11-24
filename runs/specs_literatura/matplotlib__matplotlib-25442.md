## Summary

When matplotlib 3.7.1 is used with `mplcursors`, clicking a few data points raises `AttributeError: 'NoneType' object has no attribute 'canvas'`. After the first occurrence, every new data-point selection raises the same traceback. Otherwise the cursor works. Matplotlib 3.7.0 and lower do not have this problem.

## Steps to reproduce

1. Use matplotlib 3.7.1 with the QtAgg backend and `mplcursors` installed. Installing through conda or pip gives the same result.
2. Run the script shown under "Code example." It draws a scatter plot of 10 points and attaches an `mplcursors` cursor.
3. In the plot window, click several data points one after another to select them.
4. Watch the terminal. After a few clicks the traceback appears.
5. Click another data point. The same traceback appears again on each new selection.

## Observed behavior

After a few data points have been selected, an `AttributeError: 'NoneType' object has no attribute 'canvas'` traceback is printed to the terminal. From then on, every new data-point selection prints the same traceback. Apart from these errors, `mplcursors` works.

## Expected behavior

No terminal output when selecting data points. This is how it behaves with matplotlib 3.7.0 and lower.

## Stack trace / error output

```
Traceback (most recent call last):
  File "C:\Users\MrAni\Python\miniconda3\lib\site-packages\matplotlib\cbook\__init__.py", line 304, in process
    func(*args, **kwargs)
  File "C:\Users\MrAni\Python\miniconda3\lib\site-packages\matplotlib\offsetbox.py", line 1550, in on_release
    if self._check_still_parented() and self.got_artist:
  File "C:\Users\MrAni\Python\miniconda3\lib\site-packages\matplotlib\offsetbox.py", line 1560, in _check_still_parented
    self.disconnect()
  File "C:\Users\MrAni\Python\miniconda3\lib\site-packages\matplotlib\offsetbox.py", line 1568, in disconnect
    self.canvas.mpl_disconnect(cid)
  File "C:\Users\MrAni\Python\miniconda3\lib\site-packages\matplotlib\offsetbox.py", line 1517, in <lambda>
    canvas = property(lambda self: self.ref_artist.figure.canvas)
AttributeError: 'NoneType' object has no attribute 'canvas'
```

## Test case

The original report does not include an automated test case. The script under "Code example" can be used as a manual test:

- **Run:** execute the script, then click several data points in the plot window.
- **Pass:** nothing is printed to the terminal.
- **Fail:** the `AttributeError` traceback above is printed.

## Code example

```python
import numpy as np
import matplotlib.pyplot as plt
import mplcursors as mpl

x = np.arange(1, 11)
y1 = x

plt.scatter(x, y1)

mpl.cursor()
plt.show()
```

## Version and environment

- **Matplotlib:** 3.7.1 (affected). 3.7.0 and lower work fine.
- **Backend:** QtAgg
- **Python:** 3.9.16
- **Operating system:** Windows 11 and Windows 10
- **Installation:** conda. A pip install gives the same result.
- **mplcursors version:** Not provided in the original report.
- **Jupyter:** Not provided in the original report.
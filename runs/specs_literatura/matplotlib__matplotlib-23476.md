## Summary

On an M1 (arm64) Mac using the MacOSX backend, a Matplotlib figure's `dpi` doubles every time the figure is unpickled. If a figure is repeatedly pickled and unpickled, the DPI grows exponentially until unpickling fails with `OverflowError: signed integer is greater than maximum`. The reporter says this happens every time, seems to happen only on M1 MacBooks, and occurs regardless of the Python version.

## Steps to reproduce

1. On an M1 Mac, use Matplotlib 3.5.2 with the `MacOSX` backend.
2. Create a figure with `plt.figure()`.
3. Pickle the figure to a file (`sinus.pickle`) with `pickle.dump`.
4. Load it back with `pickle.load` and read `dpi` on the loaded figure.
5. Repeat steps 3–4 on the loaded figure in a loop (the report uses 32 iterations), printing `fig.dpi` each time.
6. Observe that the DPI doubles on every round trip. After about 22 iterations, unpickling raises `OverflowError`.

## Observed behavior

The figure's DPI doubles after each unpickle: 200.0, 400.0, 800.0, … up to 419430400.0 at iteration 21. On the next unpickle, re-creating the MacOSX canvas in `Figure.__setstate__` fails with `OverflowError: signed integer is greater than maximum`.

Full output:

```
MacOSX
Matplotlib ver: 3.5.2
Platform: macOS-12.4-arm64-arm-64bit
System: Darwin
Release: 21.5.0
Python ver: 3.9.12
0: 200.0
1: 400.0
2: 800.0
3: 1600.0
4: 3200.0
5: 6400.0
6: 12800.0
7: 25600.0
8: 51200.0
9: 102400.0
10: 204800.0
11: 409600.0
12: 819200.0
13: 1638400.0
14: 3276800.0
15: 6553600.0
16: 13107200.0
17: 26214400.0
18: 52428800.0
19: 104857600.0
20: 209715200.0
21: 419430400.0
```

## Expected behavior

Unpickling should not change the figure's DPI. The DPI should stay at its original value (200.0 in the reporter's run) on every round trip, and no error should occur:

```
MacOSX
Matplotlib ver: 3.5.2
Platform: macOS-12.4-arm64-arm-64bit
System: Darwin
Release: 21.5.0
Python ver: 3.9.12
0: 200.0
1: 200.0
2: 200.0
...
21: 200.0
22: 200.0
```

## Stack trace / error output

```
Traceback (most recent call last):
  File "/Users/wsykala/projects/matplotlib/example.py", line 34, in <module>
    run()
  File "/Users/wsykala/projects/matplotlib/example.py", line 30, in run
    fig, dpi = dump_load_get_dpi(fig)
  File "/Users/wsykala/projects/matplotlib/example.py", line 20, in dump_load_get_dpi
    fig2 = pickle.load(blob)
  File "/Users/wsykala/miniconda3/envs/playground/lib/python3.9/site-packages/matplotlib/figure.py", line 2911, in __setstate__
    mgr = plt._backend_mod.new_figure_manager_given_figure(num, self)
  File "/Users/wsykala/miniconda3/envs/playground/lib/python3.9/site-packages/matplotlib/backend_bases.py", line 3499, in new_figure_manager_given_figure
    canvas = cls.FigureCanvas(figure)
  File "/Users/wsykala/miniconda3/envs/playground/lib/python3.9/site-packages/matplotlib/backends/backend_macosx.py", line 32, in __init__
    _macosx.FigureCanvas.__init__(self, width, height)
OverflowError: signed integer is greater than maximum
```

## Test case

This minimal test is derived from the reproduction script. Run it with the MacOSX backend on an M1 Mac.

```python
import pickle
import matplotlib.pyplot as plt


def test_dpi_unchanged_after_unpickle():
    fig = plt.figure()
    original_dpi = fig.dpi
    for _ in range(32):
        fig = pickle.loads(pickle.dumps(fig))
        assert fig.dpi == original_dpi
```

## Code example

The original reproduction script from the report:

```python
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pickle
import platform

print(matplotlib.get_backend())
print('Matplotlib ver:', matplotlib.__version__)
print('Platform:', platform.platform())
print('System:', platform.system())
print('Release:', platform.release())
print('Python ver:', platform.python_version())


def dump_load_get_dpi(fig):
    with open('sinus.pickle','wb') as file:
        pickle.dump(fig, file)

    with open('sinus.pickle', 'rb') as blob:
        fig2 = pickle.load(blob)
    return fig2, fig2.dpi


def run():
    fig = plt.figure()
    x = np.linspace(0,2*np.pi)
    y = np.sin(x)

    for i in range(32):
        print(f'{i}: {fig.dpi}')
        fig, dpi = dump_load_get_dpi(fig)


if __name__ == '__main__':
    run()
```

## Version and environment

- Matplotlib: 3.5.2 (installed via pip; traceback paths show a miniconda environment)
- Backend: MacOSX
- Python: 3.9.12 (the reporter says the Python version doesn't matter)
- OS: macOS 12.4 (Darwin 21.5.0), platform `macOS-12.4-arm64-arm-64bit`
- Hardware: M1 MacBook (the reporter says the issue seems to occur only on M1 MacBooks)
- Jupyter: Not provided in the original report.
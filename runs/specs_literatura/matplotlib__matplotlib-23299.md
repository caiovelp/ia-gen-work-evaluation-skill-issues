## Summary

Calling `matplotlib.get_backend()` removes all figures from `Gcf` (`plt._pylab_helpers.Gcf.figs`) if the *first* figure in `Gcf.figs` was created inside an `rc_context`. Afterward, operations that depend on `Gcf` stop working. For example, `plt.close(fig2)` has no effect because `Gcf.destroy_fig()` can't find the figure.

## Steps to reproduce

1. Make sure no figures exist yet. Do not create a figure before step 2, and do not call `plt.ion()`.
2. Create a figure inside `with rc_context():` using `plt.figure()`.
3. Record the `id()` of `plt._pylab_helpers.Gcf` and the contents of `Gcf.figs`.
4. Call `matplotlib.get_backend()`.
5. Record the `id()` of `Gcf` and the contents of `Gcf.figs` again, then compare them with step 3.

The reporter notes that the problem does **not** occur if either of these is done before the `rc_context` block:
- a figure is created outside the `rc_context` first (`fig1 = plt.figure()`), or
- `plt.ion()` is called.

## Observed behavior

The `Gcf` object is the same (identical `id`). However, `Gcf.figs` changes from containing the figure (`OrderedDict([(1, <FigureManagerQT ...>)])`) to an empty `OrderedDict()` after `get_backend()` is called. The figure is no longer tracked by `Gcf`, so `plt.close(fig2)` doesn't work.

## Expected behavior

Calling `get_backend()` should not change `Gcf.figs`. The figure created under `rc_context` should remain registered in `Gcf`, and `plt.close(fig2)` should work.

## Stack trace / error output

```
---------------------------------------------------------------------------
AssertionError                            Traceback (most recent call last)
<ipython-input-1-fa4d099aa289> in <cell line: 11>()
      9 after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
     10 
---> 11 assert before == after, '\n' + before + '\n' + after
     12 

AssertionError: 
94453354309744 OrderedDict([(1, <matplotlib.backends.backend_qt.FigureManagerQT object at 0x7fb33e26c220>)])
94453354309744 OrderedDict()
```

## Test case

Minimal test derived from the reproduction snippet in the report:

```python
import matplotlib.pyplot as plt
from matplotlib import get_backend, rc_context


def test_get_backend_keeps_figures_created_in_rc_context():
    with rc_context():
        fig2 = plt.figure()
    before = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
    get_backend()
    after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
    assert before == after, '\n' + before + '\n' + after
```

The test must run with no pre-existing figures and without `plt.ion()` being called beforehand.

## Code example

Original reproduction script from the report:

```python
import matplotlib.pyplot as plt
from matplotlib import get_backend, rc_context

# fig1 = plt.figure()  # <- UNCOMMENT THIS LINE AND IT WILL WORK
# plt.ion()            # <- ALTERNATIVELY, UNCOMMENT THIS LINE AND IT WILL ALSO WORK
with rc_context():
    fig2 = plt.figure()
before = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'
get_backend()
after = f'{id(plt._pylab_helpers.Gcf)} {plt._pylab_helpers.Gcf.figs!r}'

assert before == after, '\n' + before + '\n' + after
```

## Version and environment

- Matplotlib version: 3.5.2
- Matplotlib backend: QtAgg
- Python version: 3.10.4
- Operating system: Xubuntu
- Jupyter version: n/a (the traceback shows an IPython input cell)
- Installation: conda
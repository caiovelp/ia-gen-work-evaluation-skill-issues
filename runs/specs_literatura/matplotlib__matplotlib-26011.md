## Summary

When axes share an x-axis (via `sharex=`), the `"xlim_changed"` callbacks registered on a sibling axes are not called if the limit change comes from another axes in the shared group. The callbacks only fire on the axes where `set_xlim` was called directly.

## Steps to reproduce

1. Create two axes that share the x-axis using `sharex=`.
2. Register an `"xlim_changed"` callback on one of the axes (axes B).
3. Change the x-limits on the other axes (axes A), for example by calling `set_xlim` on it.
4. Check whether the callback registered on axes B was called.

## Observed behavior

The x-limits of axes B are updated to match axes A, but the `"xlim_changed"` callback on axes B is not called.

The reporter traced this to `set_xlim` in `lib/matplotlib/axes/_base.py`. When `emit` is true, the method processes `'xlim_changed'` for the axes itself. It then calls `set_xlim` on each shared sibling with `emit=False`. Because the sibling's `set_xlim` runs with `emit=False`, the sibling's `'xlim_changed'` callbacks are skipped.

## Expected behavior

The `"xlim_changed"` callbacks registered on an axes should be called whenever that axes' x-limits change. This includes changes that come from a shared axes. These callbacks are meant to react to any change in axis limits.

## Stack trace / error output

Not provided in the original report.

## Test case

Not provided in the original report.

## Code example

Relevant excerpt quoted in the report, from `matplotlib/lib/matplotlib/axes/_base.py`:

```python
def set_xlim(...)
    # ...
        if emit:
            self.callbacks.process('xlim_changed', self)
            # Call all of the other x-axes that are shared with this one
            for other in self._shared_x_axes.get_siblings(self):
                if other is not self:
                    other.set_xlim(self.viewLim.intervalx,
                                   emit=False, auto=auto)
```

## Version and environment

Not provided in the original report.
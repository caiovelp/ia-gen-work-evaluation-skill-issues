# Spec: Avoid `AttributeError` in `DraggableBase.disconnect` when the dragged artist has been removed from its figure

## Objective

**Problem.** On matplotlib 3.7.1, interactive use with the third-party `mplcursors` library raises a traceback after the user clicks several data points:

```
AttributeError: 'NoneType' object has no attribute 'canvas'
```

From then on, every new data-point selection raises the same traceback. Matplotlib 3.7.0 and earlier do not show this behavior.

**Failure path (from the traceback in the issue, `matplotlib/offsetbox.py`):**

1. A mouse-release event calls `on_release` (line ~1550).
2. `on_release` calls `self._check_still_parented()`.
3. The artist is no longer parented, so `_check_still_parented` calls `self.disconnect()` (line ~1560).
4. `disconnect` calls `self.canvas.mpl_disconnect(cid)` (line ~1568).
5. `canvas` is a property defined as `lambda self: self.ref_artist.figure.canvas` (line ~1517).
6. `ref_artist.figure` is `None` because the artist has been removed, so the call raises `AttributeError`.

The disconnect step runs because the artist is no longer in a figure. That same condition makes `canvas` unresolvable. As a result, the callbacks are never disconnected, and the error repeats on every later release event.

**Users affected:**
- End users of interactive matplotlib figures, including through libraries such as `mplcursors` that create draggable annotations and remove them later.
- Downstream library maintainers who depend on draggable offsetbox and annotation behavior.

**Success means:**
- Removing a draggable artist from its figure, followed by more mouse events, produces no traceback.
- Event callbacks registered by the draggable helper are cleanly disconnected.
- The reproduction from the issue runs silently.

### Acceptance criteria / user stories

- As a user running the issue's reproduction script on the QtAgg backend, I can click many data points in a row and see no terminal output.
- As a developer, when a draggable helper's reference artist is removed from its figure, `disconnect()` completes without raising, even though `ref_artist.figure` is `None`.
- After that disconnect, later mouse events on the original canvas no longer call the helper's handlers.

## Assumptions

1. **The bug is in matplotlib, not in `mplcursors`.** The fix belongs in matplotlib's `offsetbox.py` draggable machinery (the class that defines `on_release`, `_check_still_parented`, `disconnect` and the `canvas` property, presumably `DraggableBase`).
2. **A 3.7.0 → 3.7.1 change introduced the regression.** That change likely turned `canvas` from a stored attribute into a property derived from `ref_artist.figure`. This is inferred from the version boundary and the lambda in the traceback; it has not been verified.
3. **The canvas needed for disconnection is the one active when callbacks were connected.** It can be recovered without going through `ref_artist.figure`.
4. **The behavior is backend-independent.** It was reported on QtAgg, Windows 10 and Windows 11, and Python 3.9.16, but the faulty code path contains nothing OS- or backend-specific.
5. **The fix should keep the public behavior and API of the draggable classes** (`DraggableAnnotation`, `DraggableOffsetBox`, and any other subclasses) unchanged, apart from removing the error.
6. **The fix targets the matplotlib maintenance branch for 3.7.x.** It may also apply to `main`.

## Tech Stack

- **Language:** Python. Python 3.9.16 is the reported environment; the project's minimum supported Python version is unknown.
- **Library:** matplotlib 3.7.1, module `matplotlib/offsetbox.py`, plus `matplotlib/cbook` for callback processing.
- **Third-party trigger:** `mplcursors` (version unknown) and `numpy`.
- **Reported backend:** QtAgg.

## Commands

The issue does not provide any repository commands. All of the following are **unknown** and must be confirmed:

```
Build:   unknown
Test:    unknown (likely pytest-based; exact invocation and flags unknown)
Lint:    unknown
Dev:     unknown
```

Manual reproduction, taken from the issue (requires `mplcursors` and an interactive backend):

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

## Project Structure

Only the following is known from the traceback:

```
lib/.../matplotlib/offsetbox.py         → Draggable helper classes (site of the bug)
lib/.../matplotlib/cbook/__init__.py    → Callback registry `process` (where the exception surfaces)
```

The source-tree root and the test directory layout are **unknown**. The test module is presumably the one covering `offsetbox`, but its path is unknown.

## Code Style

Unknown; the project's style guide was not visible. Follow the existing conventions in `offsetbox.py`:
- Keep private helpers underscore-prefixed, as in `_check_still_parented`.
- Make minimal, local changes.

No snippet is provided, because writing the fix is out of scope.

## Testing Strategy

- **Framework:** unknown (presumably pytest).
- **Unit / regression test (required).** The test should:
  - Create a figure with a draggable artist, such as a draggable annotation or offsetbox.
  - Remove the artist from the figure.
  - Simulate a mouse button-release event through the canvas callback system.
  - Assert that no exception is raised.
  - Assert that the helper's callbacks are disconnected, for example by firing another event and confirming the handlers are not called.
- **Edge cases to cover:**
  - `disconnect()` called directly while the artist is still parented. This is existing behavior and must remain unchanged.
  - `disconnect()` called after the artist is removed.
  - `disconnect()` called twice, which should be idempotent if the existing behavior is already idempotent (unknown).
  - A release event while a drag is in progress (`got_artist` true) and the artist is removed mid-drag.
- **Headless:** the test must not require an interactive backend or `mplcursors`. It should use a non-interactive/Agg canvas and synthetic events.
- **Manual check:** run the issue's reproduction script with QtAgg and `mplcursors`, click 10 or more points, and confirm there is no terminal output.
- **Coverage expectations:** unknown.

## Boundaries

**Always:**
- Add a regression test that fails on 3.7.1 behavior and passes after the fix.
- Run the existing `offsetbox` and draggable test suites.
- Keep the fix confined to the draggable helper logic.

**Ask first:**
- Changing the public API or attributes of `DraggableBase` and its subclasses. This includes the `canvas` attribute/property semantics that third parties such as `mplcursors` may read.
- Changes that reach outside `offsetbox.py`, such as the `cbook` callback registry.
- Adding an API-change or what's-new note.
- Backport policy (3.7.x versus `main` only).

**Never:**
- Silence the error by broadly catching `AttributeError` or all exceptions in `cbook.process`.
- Leave callbacks connected after the artist is gone, which would leak handlers.
- Add a dependency on `mplcursors` in the test suite.
- Fix this by patching `mplcursors`.

## Success Criteria

1. The issue's reproduction script, run on the fixed build with QtAgg, produces no traceback after any number of point selections.
2. With a draggable helper whose `ref_artist.figure` is `None`, `disconnect()` returns without raising.
3. After that, all callback ids the helper registered are removed from the original canvas's callback registry.
4. The new regression test passes, and every existing `offsetbox`/draggable test still passes.
5. Dragging annotations and offsetboxes behaves the same as in 3.7.0 for parented artists: press, motion and release all work, and blitting/`use_blit` behavior is unchanged.
6. Code that reads `draggable.canvas` while the artist is still parented gets the same object as before.

## Open Questions

1. **What changed between 3.7.0 and 3.7.1?** Which change in `offsetbox.py` introduced the `canvas` property? Should the fix restore the earlier semantics (a stored canvas reference) or make the property tolerate a missing figure?
2. **What should `draggable.canvas` return after the artist is removed?** Options are `None`, the original canvas, or raising. Does `mplcursors` or other downstream code read this attribute?
3. **Which branch should this target?** Should the fix be backported to a 3.7.2 patch release?
4. **Can the original canvas differ from the current one?** For example, could the figure be re-attached to a new canvas or backend? If so, which canvas should `disconnect` use?
5. **Should `_check_still_parented` stay the place that triggers disconnection?** Or should disconnection also happen when the artist is removed?
6. **Is a changelog or API-change note required for this bug fix?**
7. **What are the repository's test command, test file location and CI requirements?** All are unknown from the issue.
8. **Which `mplcursors` version did the reporter use?** Does any newer `mplcursors` already work around this behavior?